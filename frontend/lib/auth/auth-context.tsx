'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface User {
  id: string;
  email: string;
  full_name: string;
  company?: string;
  role: string;
  last_login?: string;
}

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
}

interface AuthContextType extends AuthState {
  login: (email: string, password: string) => Promise<{ success: boolean; error?: string }>;
  register: (userData: RegisterData) => Promise<{ success: boolean; error?: string }>;
  logout: () => void;
  refreshAccessToken: () => Promise<boolean>;
}

interface RegisterData {
  email: string;
  password: string;
  full_name: string;
  company?: string;
}

interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const API_BASE_URL = 'http://localhost:8001';

export function AuthProvider({ children }: { children: ReactNode }) {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    accessToken: null,
    refreshToken: null,
    isLoading: true,
    isAuthenticated: false,
  });

  // Initialize auth state from localStorage
  useEffect(() => {
    const initializeAuth = () => {
      try {
        const storedUser = localStorage.getItem('netz_user');
        const storedAccessToken = localStorage.getItem('netz_access_token');
        const storedRefreshToken = localStorage.getItem('netz_refresh_token');

        if (storedUser && storedAccessToken && storedRefreshToken) {
          const user = JSON.parse(storedUser);
          setAuthState({
            user,
            accessToken: storedAccessToken,
            refreshToken: storedRefreshToken,
            isLoading: false,
            isAuthenticated: true,
          });

          // Verify token is still valid
          verifyToken(storedAccessToken);
        } else {
          setAuthState(prev => ({ ...prev, isLoading: false }));
        }
      } catch (error) {
        console.error('Error initializing auth:', error);
        clearAuthData();
        setAuthState(prev => ({ ...prev, isLoading: false }));
      }
    };

    initializeAuth();
  }, []);

  const verifyToken = async (token: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        // Token is invalid, try to refresh
        const refreshed = await refreshAccessToken();
        if (!refreshed) {
          logout();
        }
      }
    } catch (error) {
      console.error('Token verification failed:', error);
      logout();
    }
  };

  const login = async (email: string, password: string): Promise<{ success: boolean; error?: string }> => {
    try {
      setAuthState(prev => ({ ...prev, isLoading: true }));

      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      const data: LoginResponse | { detail: string } = await response.json();

      if (response.ok && 'access_token' in data) {
        const loginData = data as LoginResponse;
        
        // Store tokens and user data
        localStorage.setItem('netz_user', JSON.stringify(loginData.user));
        localStorage.setItem('netz_access_token', loginData.access_token);
        localStorage.setItem('netz_refresh_token', loginData.refresh_token);

        setAuthState({
          user: loginData.user,
          accessToken: loginData.access_token,
          refreshToken: loginData.refresh_token,
          isLoading: false,
          isAuthenticated: true,
        });

        return { success: true };
      } else {
        const errorData = data as { detail: string };
        setAuthState(prev => ({ ...prev, isLoading: false }));
        return { success: false, error: errorData.detail || 'Erreur de connexion' };
      }
    } catch (error) {
      setAuthState(prev => ({ ...prev, isLoading: false }));
      return { success: false, error: 'Erreur de connexion au serveur' };
    }
  };

  const register = async (userData: RegisterData): Promise<{ success: boolean; error?: string }> => {
    try {
      setAuthState(prev => ({ ...prev, isLoading: true }));

      const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      });

      const data: LoginResponse | { detail: string } = await response.json();

      if (response.ok && 'access_token' in data) {
        const registerData = data as LoginResponse;
        
        // Store tokens and user data
        localStorage.setItem('netz_user', JSON.stringify(registerData.user));
        localStorage.setItem('netz_access_token', registerData.access_token);
        localStorage.setItem('netz_refresh_token', registerData.refresh_token);

        setAuthState({
          user: registerData.user,
          accessToken: registerData.access_token,
          refreshToken: registerData.refresh_token,
          isLoading: false,
          isAuthenticated: true,
        });

        return { success: true };
      } else {
        const errorData = data as { detail: string };
        setAuthState(prev => ({ ...prev, isLoading: false }));
        return { success: false, error: errorData.detail || 'Erreur d\'inscription' };
      }
    } catch (error) {
      setAuthState(prev => ({ ...prev, isLoading: false }));
      return { success: false, error: 'Erreur de connexion au serveur' };
    }
  };

  const refreshAccessToken = async (): Promise<boolean> => {
    try {
      const refreshToken = authState.refreshToken || localStorage.getItem('netz_refresh_token');
      
      if (!refreshToken) {
        return false;
      }

      const response = await fetch(`${API_BASE_URL}/api/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (response.ok) {
        const data: LoginResponse = await response.json();
        
        localStorage.setItem('netz_access_token', data.access_token);
        localStorage.setItem('netz_user', JSON.stringify(data.user));

        setAuthState(prev => ({
          ...prev,
          user: data.user,
          accessToken: data.access_token,
          isAuthenticated: true,
        }));

        return true;
      } else {
        return false;
      }
    } catch (error) {
      console.error('Token refresh failed:', error);
      return false;
    }
  };

  const clearAuthData = () => {
    localStorage.removeItem('netz_user');
    localStorage.removeItem('netz_access_token');
    localStorage.removeItem('netz_refresh_token');
  };

  const logout = () => {
    clearAuthData();
    setAuthState({
      user: null,
      accessToken: null,
      refreshToken: null,
      isLoading: false,
      isAuthenticated: false,
    });
  };

  return (
    <AuthContext.Provider
      value={{
        ...authState,
        login,
        register,
        logout,
        refreshAccessToken,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}