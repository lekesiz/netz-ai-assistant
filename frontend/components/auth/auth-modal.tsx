'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Alert } from '@/components/ui/alert';
import { useAuth } from '@/lib/auth/auth-context';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialMode?: 'login' | 'register';
}

export default function AuthModal({ isOpen, onClose, initialMode = 'login' }: AuthModalProps) {
  const [mode, setMode] = useState<'login' | 'register'>(initialMode);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    full_name: '',
    company: '',
  });
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const { login, register } = useAuth();

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      let result;
      
      if (mode === 'login') {
        result = await login(formData.email, formData.password);
      } else {
        result = await register({
          email: formData.email,
          password: formData.password,
          full_name: formData.full_name,
          company: formData.company || undefined,
        });
      }

      if (result.success) {
        setFormData({
          email: '',
          password: '',
          full_name: '',
          company: '',
        });
        onClose();
      } else {
        setError(result.error || 'Une erreur est survenue');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  const switchMode = () => {
    setMode(mode === 'login' ? 'register' : 'login');
    setError(null);
    setFormData({
      email: '',
      password: '',
      full_name: '',
      company: '',
    });
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="w-full max-w-md mx-4">
        <Card className="p-6">
          <div className="text-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900">
              {mode === 'login' ? 'Connexion' : 'Inscription'}
            </h2>
            <p className="text-gray-600 mt-2">
              {mode === 'login' 
                ? 'Connectez-vous à votre compte NETZ AI' 
                : 'Créez votre compte NETZ AI'
              }
            </p>
          </div>

          {error && (
            <Alert className="mb-4 border-red-200 bg-red-50">
              <div className="text-red-800">{error}</div>
            </Alert>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {mode === 'register' && (
              <div>
                <label htmlFor="full_name" className="block text-sm font-medium text-gray-700 mb-1">
                  Nom complet *
                </label>
                <input
                  id="full_name"
                  name="full_name"
                  type="text"
                  value={formData.full_name}
                  onChange={handleInputChange}
                  required={mode === 'register'}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Jean Dupont"
                />
              </div>
            )}

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                Email *
              </label>
              <input
                id="email"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleInputChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="votre@email.com"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                Mot de passe *
              </label>
              <input
                id="password"
                name="password"
                type="password"
                value={formData.password}
                onChange={handleInputChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="••••••••"
                minLength={6}
              />
            </div>

            {mode === 'register' && (
              <div>
                <label htmlFor="company" className="block text-sm font-medium text-gray-700 mb-1">
                  Entreprise (optionnel)
                </label>
                <input
                  id="company"
                  name="company"
                  type="text"
                  value={formData.company}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Nom de votre entreprise"
                />
              </div>
            )}

            <div className="flex space-x-3">
              <Button
                type="submit"
                disabled={isLoading}
                className="flex-1"
              >
                {isLoading ? 'Chargement...' : (mode === 'login' ? 'Se connecter' : 'S\'inscrire')}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={onClose}
                disabled={isLoading}
              >
                Annuler
              </Button>
            </div>
          </form>

          <div className="mt-4 text-center">
            <button
              type="button"
              onClick={switchMode}
              className="text-sm text-blue-600 hover:text-blue-800 underline"
              disabled={isLoading}
            >
              {mode === 'login' 
                ? 'Pas de compte ? Inscrivez-vous'
                : 'Déjà un compte ? Connectez-vous'
              }
            </button>
          </div>

          {mode === 'login' && (
            <div className="mt-4 p-3 bg-gray-50 rounded-md">
              <p className="text-xs text-gray-600">
                <strong>Compte de test:</strong><br />
                Email: test@netzinformatique.fr<br />
                Mot de passe: testpass123
              </p>
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}