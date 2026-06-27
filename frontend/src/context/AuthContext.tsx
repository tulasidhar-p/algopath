import React, { createContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import api from '../services/api';

export interface User {
  id: number;
  name: string;
  email: string;
  is_admin: boolean;
  streak_count: number;
  last_active: string | null;
  created_at: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<{ success: boolean; error?: string }>;
  register: (name: string, email: string, password: string) => Promise<{ success: boolean; error?: string }>;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const initializeAuth = async () => {
      const storedToken = localStorage.getItem('token');
      if (storedToken) {
        setToken(storedToken);
        try {
          const response = await api.get('/api/auth/me');
          if (response.data.success && response.data.data) {
            setUser(response.data.data);
          } else {
            // Token expired or invalid
            logout();
          }
        } catch (error) {
          console.error("Failed to validate active token", error);
          logout();
        }
      } else {
        logout();
      }
      setLoading(false);
    };

    initializeAuth();
  }, []);

  const login = async (email: string, password: string) => {
    try {
      const response = await api.post('/api/auth/login', { email, password });
      const resData = response.data;
      if (resData.success && resData.data) {
        const { access_token, user: userData } = resData.data;
        localStorage.setItem('token', access_token);
        setToken(access_token);
        setUser(userData);
        return { success: true };
      } else {
        return { success: false, error: resData.error || 'Login failed' };
      }
    } catch (error: any) {
      const errMsg = error.response?.data?.error || error.message || 'Server error occurred';
      return { success: false, error: errMsg };
    }
  };

  const register = async (name: string, email: string, password: string) => {
    try {
      const response = await api.post('/api/auth/register', { name, email, password });
      const resData = response.data;
      if (resData.success && resData.data) {
        const { access_token, user: userData } = resData.data;
        localStorage.setItem('token', access_token);
        setToken(access_token);
        setUser(userData);
        return { success: true };
      } else {
        return { success: false, error: resData.error || 'Registration failed' };
      }
    } catch (error: any) {
      const errMsg = error.response?.data?.error || error.message || 'Server error occurred';
      return { success: false, error: errMsg };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

