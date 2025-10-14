'use client'

import { useState, useMemo } from 'react'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { 
  MessageSquare, 
  Plus, 
  ChevronLeft, 
  ChevronRight,
  Trash2,
  Settings,
  HelpCircle,
  Upload,
  Search,
  SortAsc,
  SortDesc,
  Calendar,
  Download,
  Filter,
  BarChart3
} from 'lucide-react'
import { useChatStore } from '@/lib/store/chat-store'
import { useAuth } from '@/lib/auth/auth-context'
import { format, formatDistanceToNow } from 'date-fns'
import { fr } from 'date-fns/locale'
import { cn } from '@/lib/utils'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { ConversationStats } from './conversation-stats'

interface SidebarProps {
  isOpen: boolean
  onToggle: () => void
}

type SortOption = 'recent' | 'oldest' | 'alphabetical'

export function Sidebar({ isOpen, onToggle }: SidebarProps) {
  const { 
    conversations, 
    currentConversation, 
    createConversation,
    switchConversation,
    deleteConversation,
    exportConversation,
    searchConversations
  } = useChatStore()
  
  const { isAuthenticated, user } = useAuth()
  
  const [searchQuery, setSearchQuery] = useState('')
  const [sortBy, setSortBy] = useState<SortOption>('recent')
  const [showSearch, setShowSearch] = useState(false)
  const [showStats, setShowStats] = useState(false)

  // Filter and sort conversations
  const filteredAndSortedConversations = useMemo(() => {
    let filtered = conversations

    // Apply search filter
    if (searchQuery.trim()) {
      filtered = conversations.filter(conv => 
        conv.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        conv.messages.some(msg => 
          msg.content.toLowerCase().includes(searchQuery.toLowerCase())
        )
      )
    }

    // Apply sorting
    const sorted = [...filtered].sort((a, b) => {
      switch (sortBy) {
        case 'recent':
          return new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
        case 'oldest':
          return new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime()
        case 'alphabetical':
          return a.title.localeCompare(b.title)
        default:
          return 0
      }
    })

    return sorted
  }, [conversations, searchQuery, sortBy])

  const handleNewChat = () => {
    createConversation()
  }

  const handleDeleteConversation = (id: string, e: React.MouseEvent) => {
    e.stopPropagation()
    if (confirm('Êtes-vous sûr de vouloir supprimer cette conversation ?')) {
      deleteConversation(id)
    }
  }

  const handleExportConversation = (id: string, e: React.MouseEvent) => {
    e.stopPropagation()
    const conversation = conversations.find(c => c.id === id)
    if (conversation) {
      exportConversation(conversation)
    }
  }

  const handleSearch = (query: string) => {
    setSearchQuery(query)
  }

  const getConversationPreview = (conversation: any) => {
    const lastUserMessage = conversation.messages
      .filter((msg: any) => msg.role === 'user')
      .pop()
    
    return lastUserMessage ? lastUserMessage.content.slice(0, 50) + '...' : 'Nouvelle conversation'
  }

  const getTimeAgo = (dateString: string) => {
    try {
      return formatDistanceToNow(new Date(dateString), { 
        addSuffix: true, 
        locale: fr 
      })
    } catch {
      return format(new Date(dateString), 'dd MMM', { locale: fr })
    }
  }

  return (
    <div className={cn(
      "flex h-full flex-col bg-gray-50 dark:bg-gray-900 transition-all duration-300",
      isOpen ? "w-80" : "w-16"
    )}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b">
        {isOpen && (
          <div className="flex items-center gap-2">
            <h2 className="font-semibold text-lg">NETZ AI</h2>
            {isAuthenticated && (
              <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                {conversations.length}
              </span>
            )}
          </div>
        )}
        <Button
          variant="ghost"
          size="icon"
          onClick={onToggle}
        >
          {isOpen ? <ChevronLeft /> : <ChevronRight />}
        </Button>
      </div>

      {/* Search and Controls */}
      {isOpen && (
        <div className="p-3 space-y-2 border-b">
          {/* Search Bar */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Rechercher conversations..."
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2 text-sm border border-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          
          {/* Sort Controls */}
          <div className="flex items-center gap-2">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm" className="flex-1">
                  <Filter className="h-4 w-4 mr-2" />
                  {sortBy === 'recent' ? 'Plus récent' : 
                   sortBy === 'oldest' ? 'Plus ancien' : 'Alphabétique'}
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="start">
                <DropdownMenuItem onClick={() => setSortBy('recent')}>
                  <Calendar className="h-4 w-4 mr-2" />
                  Plus récent
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setSortBy('oldest')}>
                  <Calendar className="h-4 w-4 mr-2" />
                  Plus ancien
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setSortBy('alphabetical')}>
                  <SortAsc className="h-4 w-4 mr-2" />
                  Alphabétique
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      )}

      {/* New Chat Button */}
      <div className="p-3">
        <Button
          onClick={handleNewChat}
          className="w-full justify-start"
          variant="outline"
        >
          <Plus className="h-4 w-4 mr-2" />
          {isOpen && "Nouvelle conversation"}
        </Button>
      </div>

      {/* Conversations List */}
      <ScrollArea className="flex-1 px-3">
        <div className="space-y-1 pb-4">
          {searchQuery && isOpen && (
            <div className="text-xs text-gray-500 mb-2 px-2">
              {filteredAndSortedConversations.length} résultat(s) trouvé(s)
            </div>
          )}
          
          {filteredAndSortedConversations.map((conversation) => (
            <div
              key={conversation.id}
              className={cn(
                "group flex items-start rounded-md px-2 py-3 text-sm hover:bg-gray-100 dark:hover:bg-gray-800 cursor-pointer transition-colors",
                currentConversation === conversation.id && "bg-gray-100 dark:bg-gray-800"
              )}
              onClick={() => switchConversation(conversation.id)}
            >
              <MessageSquare className="h-4 w-4 mr-2 shrink-0 mt-0.5" />
              {isOpen && (
                <>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium truncate">{conversation.title}</p>
                    <p className="text-xs text-muted-foreground truncate mt-1">
                      {getConversationPreview(conversation)}
                    </p>
                    <div className="flex items-center gap-2 mt-1">
                      <p className="text-xs text-muted-foreground">
                        {getTimeAgo(conversation.updatedAt)}
                      </p>
                      {conversation.messages.length > 0 && (
                        <span className="text-xs bg-gray-200 text-gray-700 px-1.5 py-0.5 rounded-full">
                          {conversation.messages.length}
                        </span>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex opacity-0 group-hover:opacity-100 transition-opacity ml-2">
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="icon" className="h-8 w-8">
                          <Settings className="h-3 w-3" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem onClick={(e) => handleExportConversation(conversation.id, e)}>
                          <Download className="h-4 w-4 mr-2" />
                          Exporter
                        </DropdownMenuItem>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem 
                          onClick={(e) => handleDeleteConversation(conversation.id, e)}
                          className="text-red-600 focus:text-red-600"
                        >
                          <Trash2 className="h-4 w-4 mr-2" />
                          Supprimer
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                </>
              )}
            </div>
          ))}
          
          {filteredAndSortedConversations.length === 0 && searchQuery && isOpen && (
            <div className="text-center py-8 text-gray-500">
              <Search className="h-8 w-8 mx-auto mb-2 opacity-50" />
              <p className="text-sm">Aucune conversation trouvée</p>
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Footer */}
      <div className="border-t p-3 space-y-1">
        <Button
          variant="ghost"
          className="w-full justify-start"
          onClick={() => setShowStats(true)}
        >
          <BarChart3 className="h-4 w-4 mr-2" />
          {isOpen && "Statistiques"}
        </Button>
        <Button
          variant="ghost"
          className="w-full justify-start"
          onClick={() => window.location.href = '/documents'}
        >
          <Upload className="h-4 w-4 mr-2" />
          {isOpen && "Ajouter Documents"}
        </Button>
        <Button
          variant="ghost"
          className="w-full justify-start"
          disabled
        >
          <Settings className="h-4 w-4 mr-2" />
          {isOpen && "Paramètres"}
        </Button>
        <Button
          variant="ghost"
          className="w-full justify-start"
          disabled
        >
          <HelpCircle className="h-4 w-4 mr-2" />
          {isOpen && "Aide"}
        </Button>
      </div>

      {/* Statistics Modal */}
      <ConversationStats 
        isOpen={showStats}
        onClose={() => setShowStats(false)}
      />
    </div>
  )
}