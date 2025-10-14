'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Menu, Sun, Moon, User, LogOut, Settings } from 'lucide-react'
import { useTheme } from 'next-themes'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { useAuth } from '@/lib/auth/auth-context'
import AuthModal from '@/components/auth/auth-modal'
// import { ModelSelector } from '@/components/chat/model-selector'

interface HeaderProps {
  onMenuClick: () => void
}

export function Header({ onMenuClick }: HeaderProps) {
  const { setTheme, theme } = useTheme()
  const { user, isAuthenticated, logout, isLoading } = useAuth()
  const [authModalOpen, setAuthModalOpen] = useState(false)
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login')

  const openLoginModal = () => {
    setAuthMode('login')
    setAuthModalOpen(true)
  }

  const openRegisterModal = () => {
    setAuthMode('register')
    setAuthModalOpen(true)
  }

  const getUserInitials = (fullName: string): string => {
    return fullName
      .split(' ')
      .map(name => name.charAt(0).toUpperCase())
      .slice(0, 2)
      .join('')
  }

  const getRoleBadgeVariant = (role: string) => {
    return role === 'admin' ? 'default' : 'secondary'
  }

  return (
    <header className="flex items-center justify-between h-16 px-6 border-b bg-background">
      <div className="flex items-center gap-4">
        <Button
          variant="ghost"
          size="icon"
          onClick={onMenuClick}
          className="md:hidden"
        >
          <Menu className="h-5 w-5" />
        </Button>
        <h1 className="text-xl font-semibold">NETZ AI Assistant</h1>
      </div>

      <div className="flex items-center gap-4">
        {/* Model Selector - Temporarily disabled */}
        {/* <ModelSelector /> */}
        
        {/* Theme Toggle */}
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
        >
          <Sun className="h-5 w-5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
          <Moon className="absolute h-5 w-5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
          <span className="sr-only">Changer le thème</span>
        </Button>

        {/* Authentication Section */}
        {isLoading ? (
          <div className="w-10 h-10 rounded-full bg-gray-200 animate-pulse" />
        ) : isAuthenticated && user ? (
          /* Authenticated User Menu */
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="relative h-10 w-10 rounded-full">
                <Avatar>
                  <AvatarImage src="" />
                  <AvatarFallback className="bg-blue-500 text-white">
                    {getUserInitials(user.full_name)}
                  </AvatarFallback>
                </Avatar>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-64">
              <div className="px-2 py-2">
                <div className="flex items-center space-x-2">
                  <Avatar className="h-8 w-8">
                    <AvatarFallback className="bg-blue-500 text-white text-xs">
                      {getUserInitials(user.full_name)}
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{user.full_name}</p>
                    <p className="text-xs text-gray-500 truncate">{user.email}</p>
                  </div>
                  <Badge variant={getRoleBadgeVariant(user.role)} className="text-xs">
                    {user.role === 'admin' ? 'Admin' : 'User'}
                  </Badge>
                </div>
                {user.company && (
                  <p className="text-xs text-gray-500 mt-1 px-10">{user.company}</p>
                )}
              </div>
              <DropdownMenuSeparator />
              <DropdownMenuItem disabled>
                <Settings className="mr-2 h-4 w-4" />
                <span>Paramètres</span>
              </DropdownMenuItem>
              {user.role === 'admin' && (
                <DropdownMenuItem asChild>
                  <a href="/admin" className="flex items-center">
                    <Settings className="mr-2 h-4 w-4" />
                    <span>Administration</span>
                  </a>
                </DropdownMenuItem>
              )}
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={logout} className="text-red-600 focus:text-red-600">
                <LogOut className="mr-2 h-4 w-4" />
                <span>Déconnexion</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        ) : (
          /* Guest User - Login/Register Buttons */
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={openLoginModal}
            >
              Connexion
            </Button>
            <Button
              size="sm"
              onClick={openRegisterModal}
            >
              Inscription
            </Button>
          </div>
        )}
      </div>

      {/* Authentication Modal */}
      <AuthModal
        isOpen={authModalOpen}
        onClose={() => setAuthModalOpen(false)}
        initialMode={authMode}
      />
    </header>
  )
}