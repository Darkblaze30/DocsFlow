// src/hooks/useAuth.ts
import { useState, useCallback } from 'react';
import type { LoginFormData } from '../types/auth';

export const useAuth = () => {
  const [isLoading, setIsLoading] = useState(false);

  const checkAuth = useCallback((): boolean => {
    const token = localStorage.getItem('access_token');
    
    if (!token) {
      return false;
    }
    
    const parts = token.split('.');
    if (parts.length !== 3) {
      return false;
    }
    
    return true;
  }, []);

  const makeAuthenticatedRequest = useCallback(async (url: string, options: RequestInit = {}): Promise<Response> => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      throw new Error('No token');
    }
    
    const authOptions = {
      ...options,
      headers: {
        ...options.headers,
        'Authorization': `Bearer ${token}`
      }
    };
    
    const response = await fetch(url, authOptions);
    
    if (response.status === 401) {
      localStorage.removeItem('access_token');
      setTimeout(() => {
        window.location.replace('/login');
      }, 2000);
      throw new Error('Unauthorized');
    }
    
    return response;
  }, []);

  const login = useCallback(async (credentials: LoginFormData): Promise<void> => {
    setIsLoading(true);
    
    try {
      const formData = new FormData();
      formData.append('email', credentials.email);
      formData.append('password', credentials.password);

      const response = await fetch('/login', {
        method: 'POST',
        body: formData
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Credenciales inválidas');
      }

      if (data.access_token) {
        localStorage.setItem('access_token', data.access_token);
        
        // Verificar token
        const verifyResponse = await fetch('/verify-auth', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${data.access_token}`
          }
        });
        
        if (verifyResponse.ok) {
          console.log('Token verification successful');
          window.location.href = data.redirect_url;
        } else {
          throw new Error('Error de autenticación del token');
        }
      }
    } catch (error) {
      localStorage.removeItem('access_token');
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const logout = useCallback(async (isAutomatic = false): Promise<void> => {
    setIsLoading(true);

    try {
      const token = localStorage.getItem('access_token');
      
      if (token) {
        try {
          await fetch('/logout', {
            method: 'GET',
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });
        } catch (error) {
          console.error('Error during logout:', error);
        }
      }
      
      localStorage.clear();
      sessionStorage.clear();

      if (isAutomatic) {
        alert('Tu sesión ha expirado por inactividad. Serás redirigido al login.');
      }
      
      setTimeout(() => {
        window.location.replace('/login');
      }, 1000);
      
    } catch (error) {
      console.error('Logout error:', error);
      // Forzar logout incluso si hay error
      localStorage.clear();
      sessionStorage.clear();
      window.location.replace('/login');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const verifyToken = useCallback(async (token: string): Promise<boolean> => {
    try {
      const response = await fetch('/verify-auth', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      return response.ok;
    } catch (error) {
      console.log('Token verification error:', error);
      return false;
    }
  }, []);

  return {
    isLoading,
    checkAuth,
    makeAuthenticatedRequest,
    login,
    logout,
    verifyToken
  };
};