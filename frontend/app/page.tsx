'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { MessageSquare, BrainCircuit, Shield, Zap } from 'lucide-react'

export default function HomePage() {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(false)

  const handleGetStarted = () => {
    setIsLoading(true)
    router.push('/chat')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-16">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-gray-900 dark:text-white mb-6">
            NETZ AI Assistant
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300 mb-8 max-w-2xl mx-auto">
            Votre assistant intelligent pour NETZ Informatique. 
            Accédez instantanément aux informations de l'entreprise, 
            aux données financières et obtenez des réponses précises.
          </p>
          <Button 
            onClick={handleGetStarted}
            size="lg"
            className="text-lg px-8 py-6"
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <div className="loading-dot mr-2"></div>
                <div className="loading-dot mr-2"></div>
                <div className="loading-dot"></div>
              </>
            ) : (
              <>
                <MessageSquare className="mr-2" />
                Commencer
              </>
            )}
          </Button>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          <Card className="p-6 hover:shadow-lg transition-shadow">
            <div className="flex flex-col items-center text-center">
              <BrainCircuit className="w-12 h-12 text-blue-500 mb-4" />
              <h3 className="text-xl font-semibold mb-2">Intelligence Artificielle</h3>
              <p className="text-gray-600 dark:text-gray-400">
                Modèle Mistral optimisé pour le français avec RAG pour des réponses précises
              </p>
            </div>
          </Card>

          <Card className="p-6 hover:shadow-lg transition-shadow">
            <div className="flex flex-col items-center text-center">
              <Shield className="w-12 h-12 text-green-500 mb-4" />
              <h3 className="text-xl font-semibold mb-2">100% Sécurisé</h3>
              <p className="text-gray-600 dark:text-gray-400">
                Données hébergées localement, aucune information ne quitte vos serveurs
              </p>
            </div>
          </Card>

          <Card className="p-6 hover:shadow-lg transition-shadow">
            <div className="flex flex-col items-center text-center">
              <Zap className="w-12 h-12 text-purple-500 mb-4" />
              <h3 className="text-xl font-semibold mb-2">Données Synchronisées</h3>
              <p className="text-gray-600 dark:text-gray-400">
                Intégration PennyLane et Google Drive pour des informations toujours à jour
              </p>
            </div>
          </Card>
        </div>

        {/* Info Section */}
        <div className="mt-16 text-center">
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Développé par NETZ Informatique - Haguenau
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            Support: support@netzinformatique.fr | Tel: +33 3 67 31 02 01
          </p>
          <p className="text-xs text-gray-400 dark:text-gray-500 mt-4">
            <a href="/admin" className="hover:text-blue-500 transition-colors">
              Administration
            </a>
          </p>
        </div>
      </div>
    </div>
  )
}