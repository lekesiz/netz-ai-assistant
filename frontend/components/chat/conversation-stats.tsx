'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  BarChart3, 
  MessageSquare, 
  TrendingUp,
  Calendar,
  Download,
  X,
  FileText,
  Clock
} from 'lucide-react';
import { useChatStore } from '@/lib/store/chat-store';
import { useAuth } from '@/lib/auth/auth-context';

interface ConversationStatsProps {
  isOpen: boolean;
  onClose: () => void;
}

export function ConversationStats({ isOpen, onClose }: ConversationStatsProps) {
  const { conversations, getConversationStats, exportConversation } = useChatStore();
  const { isAuthenticated, user } = useAuth();
  const [isExporting, setIsExporting] = useState(false);

  if (!isOpen) return null;

  const stats = getConversationStats();

  const exportAllConversations = async () => {
    if (!isAuthenticated) return;
    
    setIsExporting(true);
    
    try {
      // Create comprehensive export
      const exportData = {
        user: {
          name: user?.full_name,
          email: user?.email,
          company: user?.company
        },
        exportDate: new Date().toISOString(),
        stats,
        conversations: conversations.map(conv => ({
          id: conv.id,
          title: conv.title,
          createdAt: conv.createdAt,
          updatedAt: conv.updatedAt,
          messageCount: conv.messages.length,
          messages: conv.messages
        }))
      };

      // Download JSON file
      const dataStr = JSON.stringify(exportData, null, 2);
      const dataBlob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(dataBlob);
      
      const link = document.createElement('a');
      link.href = url;
      link.download = `netz-ai-conversations-${user?.full_name?.replace(/[^a-z0-9]/gi, '_')}-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);

      // Also create a summary report
      const summaryContent = [
        `NETZ AI - Rapport de Conversations`,
        `Utilisateur: ${user?.full_name} (${user?.email})`,
        `Entreprise: ${user?.company || 'Non spécifiée'}`,
        `Date d'export: ${new Date().toLocaleString('fr-FR')}`,
        '',
        '=== STATISTIQUES ===',
        `Nombre total de conversations: ${stats.totalConversations}`,
        `Nombre total de messages: ${stats.totalMessages}`,
        `Moyenne de messages par conversation: ${stats.averageMessagesPerConversation}`,
        `Plus ancienne conversation: ${stats.oldestConversation || 'N/A'}`,
        `Plus récente conversation: ${stats.newestConversation || 'N/A'}`,
        '',
        '=== CONVERSATIONS ===',
        '',
        ...conversations.map(conv => [
          `Titre: ${conv.title}`,
          `Créée le: ${new Date(conv.createdAt).toLocaleString('fr-FR')}`,
          `Dernière activité: ${new Date(conv.updatedAt).toLocaleString('fr-FR')}`,
          `Messages: ${conv.messages.length}`,
          '---'
        ].join('\n'))
      ].join('\n');

      const summaryBlob = new Blob([summaryContent], { type: 'text/plain;charset=utf-8' });
      const summaryUrl = URL.createObjectURL(summaryBlob);
      
      const summaryLink = document.createElement('a');
      summaryLink.href = summaryUrl;
      summaryLink.download = `netz-ai-rapport-${user?.full_name?.replace(/[^a-z0-9]/gi, '_')}-${new Date().toISOString().split('T')[0]}.txt`;
      document.body.appendChild(summaryLink);
      summaryLink.click();
      document.body.removeChild(summaryLink);
      URL.revokeObjectURL(summaryUrl);

    } catch (error) {
      console.error('Export failed:', error);
    } finally {
      setIsExporting(false);
    }
  };

  const getActivityLevel = (messageCount: number) => {
    if (messageCount >= 50) return { level: 'Très actif', color: 'bg-green-500' };
    if (messageCount >= 20) return { level: 'Actif', color: 'bg-blue-500' };
    if (messageCount >= 10) return { level: 'Modéré', color: 'bg-yellow-500' };
    return { level: 'Faible', color: 'bg-gray-500' };
  };

  const getRecentConversations = () => {
    return [...conversations]
      .sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime())
      .slice(0, 5);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <div className="flex items-center gap-3">
            <BarChart3 className="h-6 w-6 text-blue-600" />
            <div>
              <h2 className="text-xl font-semibold">Statistiques des Conversations</h2>
              <p className="text-sm text-gray-600">
                Analyse de votre activité NETZ AI
              </p>
            </div>
          </div>
          <Button variant="ghost" size="icon" onClick={onClose}>
            <X className="h-5 w-5" />
          </Button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-140px)]">
          {/* User Info */}
          {isAuthenticated && user && (
            <Card className="p-4 mb-6 bg-blue-50 border-blue-200">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center text-white font-semibold">
                  {user.full_name.charAt(0).toUpperCase()}
                </div>
                <div>
                  <p className="font-medium">{user.full_name}</p>
                  <p className="text-sm text-gray-600">{user.email}</p>
                  {user.company && (
                    <p className="text-sm text-gray-600">{user.company}</p>
                  )}
                </div>
                <div className="ml-auto">
                  <Badge variant={user.role === 'admin' ? 'default' : 'secondary'}>
                    {user.role === 'admin' ? 'Administrateur' : 'Utilisateur'}
                  </Badge>
                </div>
              </div>
            </Card>
          )}

          {/* Statistics Overview */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <Card className="p-4 text-center">
              <MessageSquare className="h-8 w-8 mx-auto text-blue-600 mb-2" />
              <div className="text-2xl font-bold">{stats.totalConversations}</div>
              <div className="text-sm text-gray-600">Conversations</div>
            </Card>
            
            <Card className="p-4 text-center">
              <TrendingUp className="h-8 w-8 mx-auto text-green-600 mb-2" />
              <div className="text-2xl font-bold">{stats.totalMessages}</div>
              <div className="text-sm text-gray-600">Messages</div>
            </Card>
            
            <Card className="p-4 text-center">
              <BarChart3 className="h-8 w-8 mx-auto text-purple-600 mb-2" />
              <div className="text-2xl font-bold">{stats.averageMessagesPerConversation}</div>
              <div className="text-sm text-gray-600">Moy. par conv.</div>
            </Card>
            
            <Card className="p-4 text-center">
              <Calendar className="h-8 w-8 mx-auto text-orange-600 mb-2" />
              <div className="text-2xl font-bold">
                {conversations.length > 0 ? Math.ceil((Date.now() - new Date(conversations[0]?.createdAt).getTime()) / (1000 * 60 * 60 * 24)) : 0}
              </div>
              <div className="text-sm text-gray-600">Jours d'utilisation</div>
            </Card>
          </div>

          {/* Recent Conversations */}
          <Card className="p-4 mb-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Clock className="h-5 w-5" />
              Conversations Récentes
            </h3>
            <div className="space-y-3">
              {getRecentConversations().map((conv) => {
                const activity = getActivityLevel(conv.messages.length);
                return (
                  <div key={conv.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex-1 min-w-0">
                      <p className="font-medium truncate">{conv.title}</p>
                      <p className="text-sm text-gray-600">
                        {new Date(conv.updatedAt).toLocaleString('fr-FR')}
                      </p>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-sm font-medium">{conv.messages.length} msg</span>
                      <div className={`w-3 h-3 rounded-full ${activity.color}`} title={activity.level}></div>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => exportConversation(conv)}
                      >
                        <Download className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                );
              })}
            </div>
          </Card>

          {/* Export Section */}
          <Card className="p-4">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Export des Données
            </h3>
            <div className="space-y-3">
              <p className="text-sm text-gray-600">
                Exportez toutes vos conversations en format JSON et TXT pour sauvegarde ou analyse.
              </p>
              <div className="flex gap-3">
                <Button
                  onClick={exportAllConversations}
                  disabled={isExporting || !isAuthenticated}
                  className="flex-1"
                >
                  <Download className="h-4 w-4 mr-2" />
                  {isExporting ? 'Export en cours...' : 'Exporter Tout'}
                </Button>
                <Button
                  variant="outline"
                  onClick={() => {
                    const stats = getConversationStats();
                    console.log('Statistiques:', stats);
                    alert(`Statistiques copiées dans la console:\n\nConversations: ${stats.totalConversations}\nMessages: ${stats.totalMessages}\nMoyenne: ${stats.averageMessagesPerConversation}`);
                  }}
                >
                  <BarChart3 className="h-4 w-4 mr-2" />
                  Copier Stats
                </Button>
              </div>
              {!isAuthenticated && (
                <p className="text-xs text-amber-600">
                  ⚠️ Connectez-vous pour exporter vos données
                </p>
              )}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}