// src/components/Login/Login.tsx
import React, { useState } from 'react';
import { loginUser, verifyToken } from '../../services/authService';
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
      const loginResponse = await loginUser(formData);
      
      if (loginResponse.access_token) {
        // Guardar token en localStorage
        localStorage.setItem('access_token', loginResponse.access_token);
        
        // Verificar token
        const isValid = await verifyToken(loginResponse.access_token);
        
        if (isValid) {
          console.log('Token verification successful');
          window.location.href = loginResponse.redirect_url;
        } else {
          setError('Error de autenticación del token');
        }
      }
    } catch (err: unknown) {
        if (err instanceof Error) {
          setError(err.message);
        } else {
          setError('Error de conexión');
        }
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