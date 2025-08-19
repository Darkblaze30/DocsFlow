// src/services/authService.ts
import type { LoginFormData, LoginResponse } from '../types/auth';

export const loginUser = async (credentials: LoginFormData): Promise<LoginResponse> => {
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

  return data;
};

export const verifyToken = async (token: string): Promise<boolean> => {
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
};

export const getStoredToken = (): string | null => {
  return localStorage.getItem('access_token');
};

export const removeStoredToken = (): void => {
  localStorage.removeItem('access_token');
};