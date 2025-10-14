'use client';

import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert } from '@/components/ui/alert';

interface SystemStatus {
  system: {
    ollama_available: boolean;
    rag_available: boolean;
    cache_size: number;
    uptime: number;
  };
  services: {
    ollama: string;
    rag: string;
    cache: string;
    auth: string;
  };
  timestamp: string;
}

interface CacheStats {
  cache_stats: {
    size: number;
    max_size: number;
    hit_rate: number;
    total_requests: number;
    cache_hits: number;
  };
  timestamp: string;
}

interface SystemMonitoringProps {
  accessToken: string;
  systemStatus: SystemStatus | null;
  onRefresh: () => void;
}

export default function SystemMonitoring({ accessToken, systemStatus, onRefresh }: SystemMonitoringProps) {
  const [cacheStats, setCacheStats] = useState<CacheStats | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const fetchCacheStats = async () => {
    try {
      const response = await fetch('http://localhost:8001/api/cache/stats');
      if (response.ok) {
        const data = await response.json();
        setCacheStats(data);
      }
    } catch (error) {
      console.error('Failed to fetch cache stats:', error);
    }
  };

  const clearCache = async () => {
    if (!confirm('Êtes-vous sûr de vouloir vider le cache ? Cela peut affecter les performances temporairement.')) {
      return;
    }

    try {
      setIsLoading(true);
      const response = await fetch('http://localhost:8001/api/admin/cache/clear', {
        headers: {
          'Authorization': `Bearer ${accessToken}`
        }
      });

      if (response.ok) {
        setSuccess('Cache vidé avec succès');
        fetchCacheStats();
        onRefresh();
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Erreur lors du vidage du cache');
      }
    } catch (error) {
      setError('Erreur de connexion au serveur');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchCacheStats();
    
    // Refresh data every 30 seconds
    const interval = setInterval(() => {
      fetchCacheStats();
      onRefresh();
    }, 30000);

    return () => clearInterval(interval);
  }, [accessToken]);

  const formatUptime = (seconds: number): string => {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    
    if (days > 0) {
      return `${days}j ${hours}h ${minutes}m`;
    } else if (hours > 0) {
      return `${hours}h ${minutes}m`;
    } else {
      return `${minutes}m`;
    }
  };

  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getServiceStatusBadge = (status: string) => {
    return status === 'active' ? 'default' : 'destructive';
  };

  const clearMessages = () => {
    setError(null);
    setSuccess(null);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Monitoring Système</h2>
          <p className="text-gray-600">Surveillance en temps réel des services et performances</p>
        </div>
        
        <div className="flex space-x-3">
          <Button
            onClick={onRefresh}
            variant="outline"
            disabled={isLoading}
          >
            🔄 Actualiser
          </Button>
          <Button
            onClick={clearCache}
            variant="outline"
            disabled={isLoading}
            className="text-red-600 hover:text-red-700"
          >
            🗑️ Vider Cache
          </Button>
        </div>
      </div>

      {/* Messages */}
      {error && (
        <Alert className="border-red-200 bg-red-50">
          <div className="flex justify-between items-center">
            <span className="text-red-800">{error}</span>
            <button onClick={clearMessages} className="text-red-600 hover:text-red-800">✕</button>
          </div>
        </Alert>
      )}

      {success && (
        <Alert className="border-green-200 bg-green-50">
          <div className="flex justify-between items-center">
            <span className="text-green-800">{success}</span>
            <button onClick={clearMessages} className="text-green-600 hover:text-green-800">✕</button>
          </div>
        </Alert>
      )}

      {/* System Overview */}
      {systemStatus && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card className="p-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {formatUptime(systemStatus.system.uptime)}
              </div>
              <div className="text-sm text-gray-600">Uptime</div>
            </div>
          </Card>
          
          <Card className="p-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {systemStatus.system.cache_size}
              </div>
              <div className="text-sm text-gray-600">Éléments en cache</div>
            </div>
          </Card>
          
          <Card className="p-4">
            <div className="text-center">
              <Badge variant={systemStatus.system.ollama_available ? 'default' : 'destructive'}>
                {systemStatus.system.ollama_available ? 'AI Actif' : 'AI Inactif'}
              </Badge>
              <div className="text-sm text-gray-600 mt-1">Intelligence Artificielle</div>
            </div>
          </Card>
          
          <Card className="p-4">
            <div className="text-center">
              <Badge variant={systemStatus.system.rag_available ? 'default' : 'destructive'}>
                {systemStatus.system.rag_available ? 'RAG Actif' : 'RAG Inactif'}
              </Badge>
              <div className="text-sm text-gray-600 mt-1">Base de connaissances</div>
            </div>
          </Card>
        </div>
      )}

      {/* Services Status */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">État des Services</h3>
        {systemStatus ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {Object.entries(systemStatus.services).map(([service, status]) => (
              <div key={service} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span className="font-medium capitalize">
                  {service === 'ollama' ? 'IA (Ollama)' : 
                   service === 'rag' ? 'RAG' :
                   service === 'cache' ? 'Cache' :
                   service === 'auth' ? 'Authentification' : service}
                </span>
                <Badge variant={getServiceStatusBadge(status)}>
                  {status === 'active' ? 'Actif' : 'Inactif'}
                </Badge>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-4 text-gray-500">
            Chargement des données système...
          </div>
        )}
      </Card>

      {/* Cache Statistics */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">Statistiques Cache</h3>
        {cacheStats ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="p-4 bg-blue-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">
                {cacheStats.cache_stats.size}/{cacheStats.cache_stats.max_size}
              </div>
              <div className="text-sm text-gray-600">Utilisation Cache</div>
            </div>
            
            <div className="p-4 bg-green-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600">
                {(cacheStats.cache_stats.hit_rate * 100).toFixed(1)}%
              </div>
              <div className="text-sm text-gray-600">Taux de succès</div>
            </div>
            
            <div className="p-4 bg-purple-50 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">
                {cacheStats.cache_stats.total_requests}
              </div>
              <div className="text-sm text-gray-600">Requêtes totales</div>
            </div>
            
            <div className="p-4 bg-orange-50 rounded-lg">
              <div className="text-2xl font-bold text-orange-600">
                {cacheStats.cache_stats.cache_hits}
              </div>
              <div className="text-sm text-gray-600">Succès cache</div>
            </div>
          </div>
        ) : (
          <div className="text-center py-4 text-gray-500">
            Chargement des statistiques cache...
          </div>
        )}
      </Card>

      {/* System Information */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">Informations Système</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium text-gray-900 mb-2">Configuration</h4>
            <ul className="space-y-1 text-sm text-gray-600">
              <li>• Version API: 2.0.0 Production</li>
              <li>• Environnement: Production</li>
              <li>• Base de données: PostgreSQL</li>
              <li>• Cache: Redis + LRU</li>
              <li>• IA: Ollama + Mistral</li>
            </ul>
          </div>
          
          <div>
            <h4 className="font-medium text-gray-900 mb-2">Dernière mise à jour</h4>
            <ul className="space-y-1 text-sm text-gray-600">
              <li>• Système: {systemStatus ? new Date(systemStatus.timestamp).toLocaleString('fr-FR') : 'N/A'}</li>
              <li>• Cache: {cacheStats ? new Date(cacheStats.timestamp).toLocaleString('fr-FR') : 'N/A'}</li>
              <li>• Authentification: Actif</li>
              <li>• Monitoring: Temps réel</li>
            </ul>
          </div>
        </div>
      </Card>
    </div>
  );
}