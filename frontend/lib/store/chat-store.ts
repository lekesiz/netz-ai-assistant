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
          // Send to API
          const response = await axios.post(`${API_URL}/api/chat`, {
            messages: get().messages.concat(userMessage).map(m => ({
              role: m.role,
              content: m.content
            })),
            model: 'mistral',
            temperature: 0.7
          })

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
          set({ 
            isLoading: false, 
            error: error instanceof Error ? error.message : 'Une erreur est survenue'
          })
        }
      },

      clearError: () => set({ error: null })
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