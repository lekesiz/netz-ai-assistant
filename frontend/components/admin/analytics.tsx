'use client';

import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

interface AnalyticsData {
  conversations: {
    total: number;
    today: number;
    thisWeek: number;
    thisMonth: number;
  };
  performance: {
    avgResponseTime: number;
    cacheHitRate: number;
    errorRate: number;
    uptime: number;
  };
  users: {
    total: number;
    active: number;
    newThisMonth: number;
  };
  popular_queries: {
    query: string;
    count: number;
  }[];
}

interface AnalyticsProps {
  accessToken: string;
}

export default function Analytics({ accessToken }: AnalyticsProps) {
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState<'today' | 'week' | 'month'>('week');

  // Mock data for demonstration (replace with real API calls)
  const generateMockData = (): AnalyticsData => {
    return {
      conversations: {
        total: 1247,
        today: 23,
        thisWeek: 156,
        thisMonth: 478
      },
      performance: {
        avgResponseTime: 1.42,
        cacheHitRate: 0.847,
        errorRate: 0.003,
        uptime: 99.9
      },
      users: {
        total: 2,
        active: 2,
        newThisMonth: 1
      },
      popular_queries: [
        { query: "Quels sont vos tarifs?", count: 89 },
        { query: "Comment contacter NETZ?", count: 67 },
        { query: "Formations disponibles", count: 45 },
        { query: "Chiffre d'affaires", count: 34 },
        { query: "Services de maintenance", count: 28 }
      ]
    };
  };

  useEffect(() => {
    // Simulate API call
    setIsLoading(true);
    setTimeout(() => {
      setAnalyticsData(generateMockData());
      setIsLoading(false);
    }, 1000);
  }, [accessToken]);

  const formatNumber = (num: number): string => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
  };

  const formatPercentage = (num: number): string => {
    return (num * 100).toFixed(1) + '%';
  };

  const getConversationCount = (period: string): number => {
    if (!analyticsData) return 0;
    
    switch (period) {
      case 'today': return analyticsData.conversations.today;
      case 'week': return analyticsData.conversations.thisWeek;
      case 'month': return analyticsData.conversations.thisMonth;
      default: return analyticsData.conversations.total;
    }
  };

  if (isLoading) {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          <span className="ml-2 text-gray-600">Chargement des analytiques...</span>
        </div>
      </Card>
    );
  }

  if (!analyticsData) {
    return (
      <Card className="p-6">
        <div className="text-center py-8 text-gray-500">
          Aucune donnée analytique disponible
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Analytiques & Rapports</h2>
          <p className="text-gray-600">Analyse des performances et utilisation du système</p>
        </div>
        
        <div className="flex space-x-2">
          {['today', 'week', 'month'].map((period) => (
            <Button
              key={period}
              variant={selectedPeriod === period ? 'default' : 'outline'}
              size="sm"
              onClick={() => setSelectedPeriod(period as any)}
            >
              {period === 'today' ? 'Aujourd\'hui' : 
               period === 'week' ? 'Cette semaine' : 'Ce mois'}
            </Button>
          ))}
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600">
              {formatNumber(getConversationCount(selectedPeriod))}
            </div>
            <div className="text-sm text-gray-600">Conversations</div>
            <div className="text-xs text-gray-500 mt-1">
              {selectedPeriod === 'today' ? 'Aujourd\'hui' : 
               selectedPeriod === 'week' ? 'Cette semaine' : 'Ce mois'}
            </div>
          </div>
        </Card>
        
        <Card className="p-4">
          <div className="text-center">
            <div className="text-3xl font-bold text-green-600">
              {analyticsData.performance.avgResponseTime}s
            </div>
            <div className="text-sm text-gray-600">Temps de réponse</div>
            <div className="text-xs text-green-500 mt-1">Excellent</div>
          </div>
        </Card>
        
        <Card className="p-4">
          <div className="text-center">
            <div className="text-3xl font-bold text-purple-600">
              {formatPercentage(analyticsData.performance.cacheHitRate)}
            </div>
            <div className="text-sm text-gray-600">Taux cache</div>
            <div className="text-xs text-purple-500 mt-1">Optimal</div>
          </div>
        </Card>
        
        <Card className="p-4">
          <div className="text-center">
            <div className="text-3xl font-bold text-orange-600">
              {analyticsData.performance.uptime}%
            </div>
            <div className="text-sm text-gray-600">Disponibilité</div>
            <div className="text-xs text-orange-500 mt-1">Production</div>
          </div>
        </Card>
      </div>

      {/* Performance Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Performance Système</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium">Temps de réponse moyen</span>
              <div className="flex items-center space-x-2">
                <div className="w-32 bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-green-500 h-2 rounded-full" 
                    style={{ width: `${Math.min((2 / analyticsData.performance.avgResponseTime) * 100, 100)}%` }}
                  ></div>
                </div>
                <span className="text-sm text-green-600">{analyticsData.performance.avgResponseTime}s</span>
              </div>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium">Taux de succès cache</span>
              <div className="flex items-center space-x-2">
                <div className="w-32 bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-purple-500 h-2 rounded-full" 
                    style={{ width: `${analyticsData.performance.cacheHitRate * 100}%` }}
                  ></div>
                </div>
                <span className="text-sm text-purple-600">
                  {formatPercentage(analyticsData.performance.cacheHitRate)}
                </span>
              </div>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium">Taux d'erreur</span>
              <div className="flex items-center space-x-2">
                <div className="w-32 bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-red-500 h-2 rounded-full" 
                    style={{ width: `${Math.max(analyticsData.performance.errorRate * 1000, 1)}%` }}
                  ></div>
                </div>
                <span className="text-sm text-red-600">
                  {formatPercentage(analyticsData.performance.errorRate)}
                </span>
              </div>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium">Disponibilité</span>
              <div className="flex items-center space-x-2">
                <div className="w-32 bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-500 h-2 rounded-full" 
                    style={{ width: `${analyticsData.performance.uptime}%` }}
                  ></div>
                </div>
                <span className="text-sm text-blue-600">{analyticsData.performance.uptime}%</span>
              </div>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Statistiques Utilisateurs</h3>
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">
                {analyticsData.users.total}
              </div>
              <div className="text-sm text-gray-600">Total</div>
            </div>
            
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600">
                {analyticsData.users.active}
              </div>
              <div className="text-sm text-gray-600">Actifs</div>
            </div>
            
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">
                {analyticsData.users.newThisMonth}
              </div>
              <div className="text-sm text-gray-600">Nouveaux</div>
            </div>
            
            <div className="text-center p-4 bg-orange-50 rounded-lg">
              <div className="text-2xl font-bold text-orange-600">
                {Math.round((analyticsData.users.active / analyticsData.users.total) * 100)}%
              </div>
              <div className="text-sm text-gray-600">Taux d'activité</div>
            </div>
          </div>
        </Card>
      </div>

      {/* Popular Queries */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">Requêtes Populaires</h3>
        <div className="space-y-3">
          {analyticsData.popular_queries.map((query, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-3">
                <Badge variant="outline" className="text-xs">
                  #{index + 1}
                </Badge>
                <span className="font-medium">{query.query}</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-16 bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-500 h-2 rounded-full" 
                    style={{ 
                      width: `${(query.count / analyticsData.popular_queries[0].count) * 100}%` 
                    }}
                  ></div>
                </div>
                <span className="text-sm font-medium text-blue-600 w-8 text-right">
                  {query.count}
                </span>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Business Intelligence Tab */}
      {activeTab === 'business' && businessData && (
        <div className="space-y-6">
          {/* NETZ Business Metrics */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <DollarSign className="h-5 w-5 text-green-600" />
              Métriques Business NETZ
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">
                  {formatCurrency(businessData.netz_business_metrics.total_revenue)}
                </div>
                <div className="text-sm text-gray-600">CA Total 2025</div>
              </div>
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">
                  {formatCurrency(businessData.netz_business_metrics.monthly_revenue)}
                </div>
                <div className="text-sm text-gray-600">CA Octobre 2025</div>
              </div>
              <div className="text-center p-4 bg-purple-50 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">
                  {businessData.netz_business_metrics.active_clients.toLocaleString()}
                </div>
                <div className="text-sm text-gray-600">Clients Actifs</div>
              </div>
              <div className="text-center p-4 bg-orange-50 rounded-lg">
                <div className="text-2xl font-bold text-orange-600">
                  {formatCurrency(businessData.ai_impact.estimated_cost_savings)}
                </div>
                <div className="text-sm text-gray-600">Économies IA</div>
              </div>
            </div>
          </Card>
          
          {/* AI Impact */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Impact de l'Intelligence Artificielle</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="text-center p-4 bg-cyan-50 rounded-lg">
                <div className="text-2xl font-bold text-cyan-600">
                  {businessData.ai_impact.total_queries_handled}
                </div>
                <div className="text-sm text-gray-600">Requêtes Traitées</div>
              </div>
              <div className="text-center p-4 bg-emerald-50 rounded-lg">
                <div className="text-2xl font-bold text-emerald-600">
                  {(businessData.ai_impact.automation_rate * 100).toFixed(1)}%
                </div>
                <div className="text-sm text-gray-600">Taux Automatisation</div>
              </div>
              <div className="text-center p-4 bg-rose-50 rounded-lg">
                <div className="text-2xl font-bold text-rose-600">
                  {businessData.ai_impact.time_saved_hours}h
                </div>
                <div className="text-sm text-gray-600">Temps Économisé</div>
              </div>
              <div className="text-center p-4 bg-amber-50 rounded-lg">
                <div className="text-2xl font-bold text-amber-600">
                  {businessData.ai_impact.customer_satisfaction}/5
                </div>
                <div className="text-sm text-gray-600">Satisfaction Client</div>
              </div>
            </div>
          </Card>
          
          {/* Growth Metrics */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Métriques de Croissance</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Croissance Mensuelle</h4>
                <div className="text-2xl font-bold text-green-600">
                  +{businessData.growth_metrics.monthly_query_growth}%
                </div>
                <div className="text-sm text-gray-600">Requêtes par mois</div>
              </div>
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Rétention Utilisateurs</h4>
                <div className="text-2xl font-bold text-blue-600">
                  {businessData.growth_metrics.user_retention}%
                </div>
                <div className="text-sm text-gray-600">Taux de rétention</div>
              </div>
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Adoption des Fonctionnalités</h4>
                <div className="space-y-2">
                  {Object.entries(businessData.growth_metrics.feature_adoption).map(([feature, rate]) => (
                    <div key={feature} className="flex justify-between items-center">
                      <span className="text-sm capitalize">{feature}</span>
                      <div className="flex items-center space-x-2">
                        <div className="w-20 bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-blue-500 h-2 rounded-full" 
                            style={{ width: `${rate}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-medium w-10">{rate}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </Card>
        </div>
      )}
      
      {/* Real-time Tab */}
      {activeTab === 'realtime' && realTimeData && (
        <div className="space-y-6">
          {/* System Health */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Activity className="h-5 w-5 text-green-600" />
              Santé du Système
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">
                  {formatUptime(realTimeData.system_health.uptime)}
                </div>
                <div className="text-sm text-gray-600">Uptime Système</div>
              </div>
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">
                  {realTimeData.system_health.memory_usage}
                </div>
                <div className="text-sm text-gray-600">Données en Mémoire</div>
              </div>
              <div className="text-center p-4 bg-red-50 rounded-lg">
                <div className="text-2xl font-bold text-red-600">
                  {realTimeData.system_health.error_count}
                </div>
                <div className="text-sm text-gray-600">Erreurs Totales</div>
              </div>
            </div>
          </Card>
          
          {/* Cache Performance */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Performance Cache</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center p-4 bg-purple-50 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">
                  {realTimeData.cache_performance.size}
                </div>
                <div className="text-sm text-gray-600">Éléments en Cache</div>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">
                  {realTimeData.cache_performance.recent_hits}
                </div>
                <div className="text-sm text-gray-600">Hits Récents</div>
              </div>
              <div className="text-center p-4 bg-orange-50 rounded-lg">
                <div className="text-2xl font-bold text-orange-600">
                  {realTimeData.cache_performance.recent_misses}
                </div>
                <div className="text-sm text-gray-600">Misses Récents</div>
              </div>
            </div>
          </Card>
          
          {/* Recent Activity */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Activité Récente</h3>
            <div className="space-y-3 max-h-64 overflow-y-auto">
              {realTimeData.recent_queries.slice(-10).map((query, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{query.query}</p>
                    <p className="text-xs text-gray-500">
                      {new Date(query.timestamp).toLocaleTimeString('fr-FR')}
                    </p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Badge variant={query.cached ? 'default' : 'secondary'}>
                      {query.cached ? 'Cache' : 'New'}
                    </Badge>
                    <span className="text-xs text-gray-500">
                      {query.response_time?.toFixed(3)}s
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}