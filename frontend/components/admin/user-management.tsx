'use client';

import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert } from '@/components/ui/alert';

interface User {
  id: string;
  email: string;
  full_name: string;
  company: string;
  role: string;
  is_active: boolean;
  created_at: string;
  last_login: string | null;
}

interface UserManagementProps {
  accessToken: string;
}

export default function UserManagement({ accessToken }: UserManagementProps) {
  const [users, setUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const fetchUsers = async () => {
    try {
      setIsLoading(true);
      const response = await fetch('http://localhost:8001/api/admin/users', {
        headers: {
          'Authorization': `Bearer ${accessToken}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setUsers(data.users);
        setError(null);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Erreur lors de la récupération des utilisateurs');
      }
    } catch (error) {
      setError('Erreur de connexion au serveur');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, [accessToken]);

  const formatDate = (dateString: string | null): string => {
    if (!dateString) return 'Jamais';
    
    return new Date(dateString).toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getRoleBadgeVariant = (role: string) => {
    switch (role) {
      case 'admin': return 'default';
      case 'user': return 'secondary';
      default: return 'outline';
    }
  };

  const getStatusBadgeVariant = (isActive: boolean) => {
    return isActive ? 'default' : 'destructive';
  };

  const clearMessages = () => {
    setError(null);
    setSuccess(null);
  };

  if (isLoading) {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          <span className="ml-2 text-gray-600">Chargement des utilisateurs...</span>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Gestion des Utilisateurs</h2>
          <p className="text-gray-600">Gérez les comptes utilisateurs et leurs permissions</p>
        </div>
        
        <div className="flex space-x-3">
          <Button
            onClick={fetchUsers}
            variant="outline"
          >
            🔄 Actualiser
          </Button>
          <Button>
            ➕ Nouvel utilisateur
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

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{users.length}</div>
            <div className="text-sm text-gray-600">Total Utilisateurs</div>
          </div>
        </Card>
        
        <Card className="p-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              {users.filter(u => u.is_active).length}
            </div>
            <div className="text-sm text-gray-600">Actifs</div>
          </div>
        </Card>
        
        <Card className="p-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">
              {users.filter(u => u.role === 'admin').length}
            </div>
            <div className="text-sm text-gray-600">Administrateurs</div>
          </div>
        </Card>
        
        <Card className="p-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-orange-600">
              {users.filter(u => u.last_login).length}
            </div>
            <div className="text-sm text-gray-600">Connectés</div>
          </div>
        </Card>
      </div>

      {/* Users Table */}
      <Card className="overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Utilisateur
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Entreprise
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Rôle
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Statut
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Dernière connexion
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {users.map((user) => (
                <tr key={user.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div>
                      <div className="text-sm font-medium text-gray-900">
                        {user.full_name}
                      </div>
                      <div className="text-sm text-gray-500">
                        {user.email}
                      </div>
                    </div>
                  </td>
                  
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-900">
                      {user.company || 'Non spécifié'}
                    </div>
                  </td>
                  
                  <td className="px-6 py-4">
                    <Badge variant={getRoleBadgeVariant(user.role)}>
                      {user.role === 'admin' ? 'Administrateur' : 'Utilisateur'}
                    </Badge>
                  </td>
                  
                  <td className="px-6 py-4">
                    <Badge variant={getStatusBadgeVariant(user.is_active)}>
                      {user.is_active ? 'Actif' : 'Inactif'}
                    </Badge>
                  </td>
                  
                  <td className="px-6 py-4 text-sm text-gray-900">
                    {formatDate(user.last_login)}
                  </td>
                  
                  <td className="px-6 py-4">
                    <div className="flex space-x-2">
                      <Button
                        size="sm"
                        variant="outline"
                        className="text-xs"
                      >
                        ✏️ Modifier
                      </Button>
                      
                      {user.role !== 'admin' && (
                        <Button
                          size="sm"
                          variant="outline"
                          className="text-xs text-red-600 hover:text-red-700"
                        >
                          🗑️ Supprimer
                        </Button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        {users.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            Aucun utilisateur trouvé
          </div>
        )}
      </Card>
    </div>
  );
}