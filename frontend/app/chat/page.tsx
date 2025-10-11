'use client'

import { useState, useEffect, useRef } from 'react'
import { ChatInterface } from '@/components/chat/chat-interface'
import { Sidebar } from '@/components/chat/sidebar'
import { Header } from '@/components/layout/header'
import { useChatStore } from '@/lib/store/chat-store'

export default function ChatPage() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true)
  const { initialize } = useChatStore()

  useEffect(() => {
    initialize()
  }, [initialize])

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <Sidebar 
        isOpen={isSidebarOpen} 
        onToggle={() => setIsSidebarOpen(!isSidebarOpen)}
      />

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        <Header 
          onMenuClick={() => setIsSidebarOpen(!isSidebarOpen)}
        />
        <main className="flex-1 overflow-hidden">
          <ChatInterface />
        </main>
      </div>
    </div>
  )
}