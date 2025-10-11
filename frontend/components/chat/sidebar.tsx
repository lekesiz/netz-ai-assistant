'use client'

import { useState } from 'react'
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
  Upload
} from 'lucide-react'
import { useChatStore } from '@/lib/store/chat-store'
import { format } from 'date-fns'
import { fr } from 'date-fns/locale'
import { cn } from '@/lib/utils'

interface SidebarProps {
  isOpen: boolean
  onToggle: () => void
}

export function Sidebar({ isOpen, onToggle }: SidebarProps) {
  const { 
    conversations, 
    currentConversation, 
    createConversation,
    switchConversation,
    deleteConversation 
  } = useChatStore()

  const handleNewChat = () => {
    createConversation()
  }

  const handleDeleteConversation = (id: string, e: React.MouseEvent) => {
    e.stopPropagation()
    if (confirm('Êtes-vous sûr de vouloir supprimer cette conversation ?')) {
      deleteConversation(id)
    }
  }

  return (
    <div className={cn(
      "flex h-full flex-col bg-gray-50 dark:bg-gray-900 transition-all duration-300",
      isOpen ? "w-64" : "w-16"
    )}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b">
        {isOpen && (
          <h2 className="font-semibold text-lg">NETZ AI</h2>
        )}
        <Button
          variant="ghost"
          size="icon"
          onClick={onToggle}
        >
          {isOpen ? <ChevronLeft /> : <ChevronRight />}
        </Button>
      </div>

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
          {conversations.map((conversation) => (
            <div
              key={conversation.id}
              className={cn(
                "group flex items-center rounded-md px-2 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-800 cursor-pointer",
                currentConversation === conversation.id && "bg-gray-100 dark:bg-gray-800"
              )}
              onClick={() => switchConversation(conversation.id)}
            >
              <MessageSquare className="h-4 w-4 mr-2 shrink-0" />
              {isOpen && (
                <>
                  <div className="flex-1 truncate">
                    <p className="truncate">{conversation.title}</p>
                    <p className="text-xs text-muted-foreground">
                      {format(new Date(conversation.updatedAt), 'dd MMM', { locale: fr })}
                    </p>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="opacity-0 group-hover:opacity-100 transition-opacity"
                    onClick={(e) => handleDeleteConversation(conversation.id, e)}
                  >
                    <Trash2 className="h-3 w-3" />
                  </Button>
                </>
              )}
            </div>
          ))}
        </div>
      </ScrollArea>

      {/* Footer */}
      <div className="border-t p-3 space-y-1">
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
    </div>
  )
}