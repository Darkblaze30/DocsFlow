// src/components/Login/Login.tsx
import React, { useState } from 'react';
import { loginUser } from '../../services/authService';
import type { LoginFormData } from '../../types/auth';
import './login.css';

const Login: React.FC = () => {
  const [formData, setFormData] = useState<LoginFormData>({
    email: '',
    password: ''
  });
  const [error, setError] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      // loginUser ya guarda el token automáticamente en localStorage
      await loginUser(formData);
      
      // Redirigir directamente al dashboard
      window.location.href = '/dashboard';
      
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Error de conexión');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="card">
        <h2>Iniciar sesión</h2>
        
        {error && (
          <div className="error" style={{ display: 'block' }}>
            {error}
          </div>
        )}
        
        <form onSubmit={handleSubmit}>
          <input
            id="email"
            name="email"
            placeholder="Correo electrónico"
            type="email"
            value={formData.email}
            onChange={handleInputChange}
            required
          />
          
          <input
            id="password"
            name="password"
            placeholder="Contraseña"
            type="password"
            value={formData.password}
            onChange={handleInputChange}
            required
          />
          
          <button type="submit" disabled={isLoading}>
            {isLoading ? 'Entrando...' : 'Entrar'}
          </button>
        </form>
        
        <p>
          ¿Olvidaste la contraseña? <a href="/password">Click aquí</a>
        </p>
      </div>
    </div>
  );
};

export default Login;