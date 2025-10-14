'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, Paperclip, Mic, StopCircle, Shield, ShieldCheck } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { ChatMessage } from './chat-message'
import { useChatStore } from '@/lib/store/chat-store'
import { useAuth } from '@/lib/auth/auth-context'
import { ScrollArea } from '@/components/ui/scroll-area'
import { TypingIndicator } from '@/components/ui/typing-indicator'

export function ChatInterface() {
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isRecording, setIsRecording] = useState(false)
  const scrollAreaRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  
  const { messages, sendMessage, currentConversation } = useChatStore()
  const { isAuthenticated, user } = useAuth()

  useEffect(() => {
    // Scroll to bottom when new messages arrive
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight
    }
  }, [messages])

  const handleSubmit = async (e?: React.FormEvent) => {
    e?.preventDefault()
    
    if (!input.trim() || isLoading) return

    const userInput = input.trim()
    setInput('')
    setIsLoading(true)

    try {
      await sendMessage(userInput)
    } catch (error) {
      console.error('Error sending message:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  const toggleRecording = () => {
    setIsRecording(!isRecording)
    // TODO: Implement voice recording
  }

  return (
    <div className="flex flex-col h-full">
      {/* Messages Area */}
      <ScrollArea 
        ref={scrollAreaRef}
        className="flex-1 px-4 py-6"
      >
        <div className="max-w-4xl mx-auto space-y-4">
          {messages.length === 0 ? (
            <div className="text-center py-12">
              <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
                Bienvenue dans NETZ AI Assistant
              </h2>
              <p className="text-gray-600 dark:text-gray-400 mb-8">
                Posez-moi vos questions sur NETZ Informatique, 
                les données financières ou tout autre sujet professionnel.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl mx-auto">
                <Button
                  variant="outline"
                  className="h-auto p-4 justify-start"
                  onClick={() => setInput("Quel est le chiffre d'affaires de ce mois ?")}
                >
                  <div className="text-left">
                    <p className="font-medium">Analyse financière</p>
                    <p className="text-sm text-muted-foreground">
                      Chiffre d'affaires et statistiques
                    </p>
                  </div>
                </Button>
                <Button
                  variant="outline"
                  className="h-auto p-4 justify-start"
                  onClick={() => setInput("Qui sont nos meilleurs clients ?")}
                >
                  <div className="text-left">
                    <p className="font-medium">Analyse clients</p>
                    <p className="text-sm text-muted-foreground">
                      Top clients et relations
                    </p>
                  </div>
                </Button>
                <Button
                  variant="outline"
                  className="h-auto p-4 justify-start"
                  onClick={() => setInput("Quels sont nos services disponibles ?")}
                >
                  <div className="text-left">
                    <p className="font-medium">Services</p>
                    <p className="text-sm text-muted-foreground">
                      Catalogue et tarifs
                    </p>
                  </div>
                </Button>
                <Button
                  variant="outline"
                  className="h-auto p-4 justify-start"
                  onClick={() => setInput("Informations sur la société NETZ")}
                >
                  <div className="text-left">
                    <p className="font-medium">Entreprise</p>
                    <p className="text-sm text-muted-foreground">
                      Informations légales et contact
                    </p>
                  </div>
                </Button>
              </div>
            </div>
          ) : (
            messages.map((message, index) => (
              <ChatMessage key={index} message={message} />
            ))
          )}
          {isLoading && <TypingIndicator />}
        </div>
      </ScrollArea>

      {/* Input Area */}
      <div className="border-t bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto p-4">
          {/* Authentication Status */}
          <div className="flex items-center justify-center mb-3">
            <Badge 
              variant={isAuthenticated ? "default" : "secondary"} 
              className="text-xs"
            >
              {isAuthenticated ? (
                <>
                  <ShieldCheck className="h-3 w-3 mr-1" />
                  Mode sécurisé - {user?.full_name}
                </>
              ) : (
                <>
                  <Shield className="h-3 w-3 mr-1" />
                  Mode invité
                </>
              )}
            </Badge>
          </div>
          <div className="flex items-end gap-2">
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className="mb-1"
              disabled
              title="Joindre un fichier (bientôt disponible)"
            >
              <Paperclip className="h-5 w-5" />
            </Button>
            
            <div className="flex-1">
              <Textarea
                ref={textareaRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Tapez votre message..."
                rows={1}
                className="min-h-[44px] max-h-[200px] resize-none"
                disabled={isLoading}
              />
            </div>

            <Button
              type="button"
              variant="ghost"
              size="icon"
              className="mb-1"
              onClick={toggleRecording}
              disabled
              title="Enregistrement vocal (bientôt disponible)"
            >
              {isRecording ? (
                <StopCircle className="h-5 w-5 text-red-500" />
              ) : (
                <Mic className="h-5 w-5" />
              )}
            </Button>

            <Button
              type="submit"
              size="icon"
              className="mb-1"
              disabled={!input.trim() || isLoading}
            >
              <Send className="h-5 w-5" />
            </Button>
          </div>
          <p className="text-xs text-muted-foreground mt-2 text-center">
            NETZ AI peut faire des erreurs. Vérifiez les informations importantes.
          </p>
        </form>
      </div>
    </div>
  )
}