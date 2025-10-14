import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import axios from 'axios'

interface Message {
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: string
  sources?: Array<{
    text: string
    metadata: any
    score: number
  }>
}

interface Conversation {
  id: string
  title: string
  createdAt: string
  updatedAt: string
  messages: Message[]
}

interface ChatState {
  conversations: Conversation[]
  currentConversation: string | null
  messages: Message[]
  isLoading: boolean
  error: string | null

  // Actions
  initialize: () => void
  createConversation: (title?: string) => string
  switchConversation: (id: string) => void
  deleteConversation: (id: string) => void
  sendMessage: (content: string) => Promise<void>
  clearError: () => void
  exportConversation: (conversation: Conversation) => void
  searchConversations: (query: string) => Conversation[]
  renameConversation: (id: string, newTitle: string) => void
  getConversationStats: () => ConversationStats
}

interface ConversationStats {
  totalConversations: number
  totalMessages: number
  averageMessagesPerConversation: number
  oldestConversation?: string
  newestConversation?: string
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'

export const useChatStore = create<ChatState>()(
  persist(
    (set, get) => ({
      conversations: [],
      currentConversation: null,
      messages: [],
      isLoading: false,
      error: null,

      initialize: () => {
        const state = get()
        if (state.conversations.length === 0) {
          const id = get().createConversation('Nouvelle conversation')
          set({ currentConversation: id })
        } else if (!state.currentConversation) {
          set({ currentConversation: state.conversations[0].id })
        }
        
        // Load messages for current conversation
        const current = state.conversations.find(c => c.id === state.currentConversation)
        if (current) {
          set({ messages: current.messages })
        }
      },

      createConversation: (title = 'Nouvelle conversation') => {
        const id = `conv_${Date.now()}`
        const newConversation: Conversation = {
          id,
          title,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          messages: []
        }

        set(state => ({
          conversations: [...state.conversations, newConversation],
          currentConversation: id,
          messages: []
        }))

        return id
      },

      switchConversation: (id: string) => {
        const conversation = get().conversations.find(c => c.id === id)
        if (conversation) {
          set({
            currentConversation: id,
            messages: conversation.messages
          })
        }
      },

      deleteConversation: (id: string) => {
        set(state => {
          const conversations = state.conversations.filter(c => c.id !== id)
          const needNewCurrent = state.currentConversation === id

          if (conversations.length === 0) {
            // Create a new conversation if all are deleted
            const newId = get().createConversation()
            return { 
              conversations: get().conversations,
              currentConversation: newId 
            }
          }

          return {
            conversations,
            currentConversation: needNewCurrent ? conversations[0].id : state.currentConversation,
            messages: needNewCurrent ? conversations[0].messages : state.messages
          }
        })
      },

      sendMessage: async (content: string) => {
        const userMessage: Message = {
          role: 'user',
          content,
          timestamp: new Date().toISOString()
        }

        // Add user message
        set(state => ({
          messages: [...state.messages, userMessage],
          isLoading: true,
          error: null
        }))

        // Update conversation
        const currentId = get().currentConversation
        if (currentId) {
          set(state => ({
            conversations: state.conversations.map(conv => 
              conv.id === currentId
                ? {
                    ...conv,
                    messages: [...conv.messages, userMessage],
                    updatedAt: new Date().toISOString(),
                    title: conv.messages.length === 0 ? content.slice(0, 50) + '...' : conv.title
                  }
                : conv
            )
          }))
        }

        try {
          // Check if user is authenticated
          const accessToken = localStorage.getItem('netz_access_token')
          const isAuthenticated = !!accessToken

          let response
          
          if (isAuthenticated) {
            // Use protected endpoint for authenticated users
            response = await axios.post(`${API_URL}/api/chat/protected`, {
              message: content,
              conversation_id: currentId,
            }, {
              headers: {
                'Authorization': `Bearer ${accessToken}`
              }
            })
          } else {
            // Use regular endpoint for guests
            response = await axios.post(`${API_URL}/api/chat`, {
              messages: get().messages.concat(userMessage).map(m => ({
                role: m.role,
                content: m.content
              })),
              model: 'mistral',
              temperature: 0.7
            })
          }

          const assistantMessage: Message = {
            role: 'assistant',
            content: response.data.response,
            timestamp: response.data.timestamp || new Date().toISOString(),
            sources: response.data.sources
          }

          // Add assistant message
          set(state => ({
            messages: [...state.messages, assistantMessage],
            isLoading: false
          }))

          // Update conversation
          if (currentId) {
            set(state => ({
              conversations: state.conversations.map(conv => 
                conv.id === currentId
                  ? {
                      ...conv,
                      messages: [...conv.messages, assistantMessage],
                      updatedAt: new Date().toISOString()
                    }
                  : conv
              )
            }))
          }
        } catch (error) {
          let errorMessage = 'Une erreur est survenue'
          
          if (axios.isAxiosError(error)) {
            if (error.response?.status === 401) {
              // Token expired or invalid, clear auth data
              localStorage.removeItem('netz_access_token')
              localStorage.removeItem('netz_refresh_token')
              localStorage.removeItem('netz_user')
              errorMessage = 'Session expirée. Veuillez vous reconnecter.'
            } else {
              errorMessage = error.response?.data?.detail || error.message
            }
          }
          
          set({ 
            isLoading: false, 
            error: errorMessage
          })
        }
      },

      clearError: () => set({ error: null }),

      exportConversation: (conversation: Conversation) => {
        const exportData = {
          id: conversation.id,
          title: conversation.title,
          createdAt: conversation.createdAt,
          updatedAt: conversation.updatedAt,
          messageCount: conversation.messages.length,
          messages: conversation.messages.map(msg => ({
            role: msg.role,
            content: msg.content,
            timestamp: msg.timestamp,
            sources: msg.sources || []
          }))
        }

        // Create downloadable file
        const dataStr = JSON.stringify(exportData, null, 2)
        const dataBlob = new Blob([dataStr], { type: 'application/json' })
        const url = URL.createObjectURL(dataBlob)
        
        const link = document.createElement('a')
        link.href = url
        link.download = `conversation-${conversation.title.replace(/[^a-z0-9]/gi, '_')}-${new Date().toISOString().split('T')[0]}.json`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        URL.revokeObjectURL(url)

        // Also create a readable text version
        const textContent = [
          `Conversation: ${conversation.title}`,
          `Créée le: ${new Date(conversation.createdAt).toLocaleString('fr-FR')}`,
          `Dernière mise à jour: ${new Date(conversation.updatedAt).toLocaleString('fr-FR')}`,
          `Nombre de messages: ${conversation.messages.length}`,
          '',
          '--- Messages ---',
          '',
          ...conversation.messages.map(msg => [
            `[${new Date(msg.timestamp).toLocaleString('fr-FR')}] ${msg.role.toUpperCase()}:`,
            msg.content,
            msg.sources && msg.sources.length > 0 ? `Sources: ${msg.sources.map(s => s.text).join(', ')}` : '',
            ''
          ].filter(Boolean).join('\n'))
        ].join('\n')

        const textBlob = new Blob([textContent], { type: 'text/plain;charset=utf-8' })
        const textUrl = URL.createObjectURL(textBlob)
        
        const textLink = document.createElement('a')
        textLink.href = textUrl
        textLink.download = `conversation-${conversation.title.replace(/[^a-z0-9]/gi, '_')}-${new Date().toISOString().split('T')[0]}.txt`
        document.body.appendChild(textLink)
        textLink.click()
        document.body.removeChild(textLink)
        URL.revokeObjectURL(textUrl)
      },

      searchConversations: (query: string) => {
        const state = get()
        if (!query.trim()) return state.conversations

        return state.conversations.filter(conv => 
          conv.title.toLowerCase().includes(query.toLowerCase()) ||
          conv.messages.some(msg => 
            msg.content.toLowerCase().includes(query.toLowerCase())
          )
        )
      },

      renameConversation: (id: string, newTitle: string) => {
        set(state => ({
          conversations: state.conversations.map(conv => 
            conv.id === id 
              ? { ...conv, title: newTitle, updatedAt: new Date().toISOString() }
              : conv
          )
        }))
      },

      getConversationStats: () => {
        const state = get()
        const totalMessages = state.conversations.reduce((total, conv) => total + conv.messages.length, 0)
        const avgMessages = state.conversations.length > 0 ? totalMessages / state.conversations.length : 0
        
        const sortedByDate = [...state.conversations].sort((a, b) => 
          new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime()
        )

        return {
          totalConversations: state.conversations.length,
          totalMessages,
          averageMessagesPerConversation: Math.round(avgMessages * 10) / 10,
          oldestConversation: sortedByDate[0]?.title,
          newestConversation: sortedByDate[sortedByDate.length - 1]?.title
        }
      }
    }),
    {
      name: 'netz-chat-storage',
      partialize: (state) => ({
        conversations: state.conversations,
        currentConversation: state.currentConversation
      })
    }
  )
)