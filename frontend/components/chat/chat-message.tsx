'use client'

import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Card } from '@/components/ui/card'
import { Bot, User, FileText, ExternalLink } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import { format } from 'date-fns'
import { fr } from 'date-fns/locale'

interface Source {
  text: string
  metadata?: {
    filename?: string
    source?: string
    type?: string
  }
  score: number
}

interface Message {
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: string
  sources?: Source[]
}

interface ChatMessageProps {
  message: Message
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user'

  return (
    <div className={`flex gap-3 ${isUser ? 'justify-end' : ''} animate-fade-in-up`}>
      {!isUser && (
        <Avatar className="h-8 w-8 mt-1">
          <AvatarImage src="/netz-logo.png" />
          <AvatarFallback>
            <Bot className="h-5 w-5" />
          </AvatarFallback>
        </Avatar>
      )}

      <div className={`flex-1 max-w-2xl ${isUser ? 'text-right' : ''}`}>
        <div className="flex items-center gap-2 mb-1">
          <span className="text-sm font-medium">
            {isUser ? 'Vous' : 'NETZ AI'}
          </span>
          <span className="text-xs text-muted-foreground">
            {format(new Date(message.timestamp), 'HH:mm', { locale: fr })}
          </span>
        </div>

        <Card className={`inline-block text-left ${isUser ? 'bg-primary text-primary-foreground' : ''}`}>
          <div className="p-3">
            {isUser ? (
              <p className="whitespace-pre-wrap">{message.content}</p>
            ) : (
              <div className="prose prose-sm dark:prose-invert max-w-none">
                <ReactMarkdown>{message.content}</ReactMarkdown>
              </div>
            )}
          </div>
        </Card>

        {/* Sources */}
        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="mt-2 space-y-1">
            <p className="text-xs text-muted-foreground">Sources:</p>
            {message.sources.map((source, idx) => (
              <div key={idx} className="flex items-center gap-2 text-xs">
                <FileText className="h-3 w-3 text-muted-foreground" />
                <span className="text-muted-foreground">
                  {source.metadata?.filename || source.metadata?.source || source.text?.slice(0, 30) + '...' || 'Document'}
                </span>
                <span className="text-muted-foreground">
                  ({(source.score * 100).toFixed(0)}% pertinent)
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

      {isUser && (
        <Avatar className="h-8 w-8 mt-1">
          <AvatarFallback>
            <User className="h-5 w-5" />
          </AvatarFallback>
        </Avatar>
      )}
    </div>
  )
}