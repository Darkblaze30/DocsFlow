// src/types/auth.ts
export interface LoginFormData {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  redirect_url: string;
  token_type?: string;
}

export interface User {
  id: string;
  email: string;
  name?: string;
  rol?: string;
}

export interface RegisterFormData {
  name: string;
  email: string;
  password: string;
  department_name: string;
  rol: string;
}

export interface Department {
  name: string;
}

export interface AuthContextType {
  user: User | null;
  login: (credentials: LoginFormData) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
  isLoading: boolean;
}