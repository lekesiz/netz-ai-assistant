'use client';

import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert } from '@/components/ui/alert';
import AdminLogin from '@/components/admin/admin-login';
import UserManagement from '@/components/admin/user-management';
import SystemMonitoring from '@/components/admin/system-monitoring';
import Analytics from '@/components/admin/analytics';

interface AdminUser {
  id: string;
  email: string;
  full_name: string;
  company: string;
  role: string;
}

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

type TabType = 'users' | 'system' | 'analytics' | 'settings';

export default function AdminDashboard() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [adminUser, setAdminUser] = useState<AdminUser | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<TabType>('users');
  const [error, setError] = useState<string | null>(null);
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);

  useEffect(() => {
    // Check if admin is already logged in (from localStorage)
    const token = localStorage.getItem('admin_token');
    const user = localStorage.getItem('admin_user');
    
    if (token && user) {
      setAccessToken(token);
      setAdminUser(JSON.parse(user));
      setIsAuthenticated(true);
      fetchSystemStatus(token);
    }
  }, []);

  const fetchSystemStatus = async (token: string) => {
    try {
      const response = await fetch('http://localhost:8001/api/admin/system/status', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const status = await response.json();
        setSystemStatus(status);
      }
    } catch (error) {
      console.error('Failed to fetch system status:', error);
    }
  };

  const handleLogin = (user: AdminUser, token: string) => {
    setAdminUser(user);
    setAccessToken(token);
    setIsAuthenticated(true);
    setError(null);
    
    // Store in localStorage for persistence
    localStorage.setItem('admin_token', token);
    localStorage.setItem('admin_user', JSON.stringify(user));
    
    // Fetch system status
    fetchSystemStatus(token);
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setAdminUser(null);
    setAccessToken(null);
    localStorage.removeItem('admin_token');
    localStorage.removeItem('admin_user');
  };

  const formatUptime = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="w-full max-w-md">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900">NETZ Admin</h1>
            <p className="text-gray-600 mt-2">Système d'administration</p>
          </div>
          
          {error && (
            <Alert className="mb-4 border-red-200 bg-red-50">
              <div className="text-red-800">{error}</div>
            </Alert>
          )}
          
          <AdminLogin onLogin={handleLogin} onError={setError} />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-bold text-gray-900">NETZ Admin Dashboard</h1>
              {systemStatus && (
                <div className="flex items-center space-x-2">
                  <Badge variant={systemStatus.services.ollama === 'active' ? 'default' : 'destructive'}>
                    AI: {systemStatus.services.ollama}
                  </Badge>
                  <Badge variant={systemStatus.services.auth === 'active' ? 'default' : 'destructive'}>
                    Auth: {systemStatus.services.auth}
                  </Badge>
                  <span className="text-sm text-gray-500">
                    Uptime: {formatUptime(systemStatus.system.uptime)}
                  </span>
                </div>
              )}
            </div>
            
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">
                {adminUser?.full_name} ({adminUser?.company})
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={handleLogout}
              >
                Déconnexion
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {[
              { key: 'users', label: 'Utilisateurs', icon: '👥' },
              { key: 'system', label: 'Système', icon: '⚙️' },
              { key: 'analytics', label: 'Analytiques', icon: '📊' },
              { key: 'settings', label: 'Paramètres', icon: '🔧' }
            ].map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key as TabType)}
                className={`py-4 px-2 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                  activeTab === tab.key
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <span>{tab.icon}</span>
                <span>{tab.label}</span>
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        {activeTab === 'users' && (
          <UserManagement accessToken={accessToken!} />
        )}
        
        {activeTab === 'system' && (
          <SystemMonitoring 
            accessToken={accessToken!} 
            systemStatus={systemStatus}
            onRefresh={() => fetchSystemStatus(accessToken!)}
          />
        )}
        
        {activeTab === 'analytics' && (
          <Analytics accessToken={accessToken!} />
        )}
        
        {activeTab === 'settings' && (
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Paramètres Système</h2>
            <p className="text-gray-600">Configuration et paramètres avancés (bientôt disponible)</p>
          </Card>
        )}
      </main>
    </div>
  );
}