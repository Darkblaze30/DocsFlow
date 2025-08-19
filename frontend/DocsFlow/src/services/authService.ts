// src/services/authService.ts
import type { LoginFormData, LoginResponse, DashboardResponse, RegisterFormDataResponse } from '../types/auth';

export const loginUser = async (credentials: LoginFormData): Promise<LoginResponse> => {
  const formData = new FormData();
  formData.append('email', credentials.email);
  formData.append('password', credentials.password);

  const response = await fetch('/api/login', {
    method: 'POST',
    body: formData
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || 'Credenciales inválidas');
  }

  // Guardar token automáticamente
  if (data.access_token) {
    localStorage.setItem('access_token', data.access_token);
  }

  return data;
};

export const verifyToken = async (token?: string): Promise<boolean> => {
  try {
    const tokenToUse = token || localStorage.getItem('access_token');
    if (!tokenToUse) return false;

    const response = await fetch('/api/verify-auth', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${tokenToUse}`
      }
    });
        
    return response.ok;
  } catch (error) {
    console.log('Token verification error:', error);
    return false;
  }
};

export const registerUser = async (formData: FormData): Promise<void> => {
  const token = localStorage.getItem('access_token');
  
  const headers: Record<string, string> = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch('/api/register', {
    method: 'POST',
    headers,
    body: formData
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Error al registrar usuario');
  }
};

export const getStoredToken = (): string | null => {
  return localStorage.getItem('access_token');
};

export const removeStoredToken = (): void => {
  localStorage.removeItem('access_token');
};

export const logout = (): void => {
  removeStoredToken();
  // Opcionalmente redirigir al login
  window.location.href = '/api/login';
};

export const getDashboardData = async (): Promise<DashboardResponse> => {
  const token = localStorage.getItem('access_token');
  if (!token) {
    throw new Error('No hay token guardado');
  }

  const response = await fetch('/api/dashboard', {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Error al obtener datos del dashboard');
  }

  return response.json() as Promise<DashboardResponse>;
};

export const getRegisterFormData = async (): Promise<RegisterFormDataResponse> => {
  const token = localStorage.getItem('access_token');
  if (!token) {
    throw new Error('No hay token guardado');
  }

  const response = await fetch('/api/register/data', {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Error al obtener datos del formulario');
  }

  return response.json();
}; 