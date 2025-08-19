// src/components/Register/Register.tsx
import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../../hooks/useAuth';
import type { RegisterFormData, Department } from '../../types/auth';
import './Register.css';

const Register: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [accessDenied, setAccessDenied] = useState(false);
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [roles, setRoles] = useState<string[]>([]);
  const { checkAuth } = useAuth();

  const [formData, setFormData] = useState<RegisterFormData>({
    name: '',
    email: '',
    password: '',
    department_name: '',
    rol: ''
  });

  const loadFormData = useCallback(async () => {
    try {
      if (!checkAuth()) {
        setTimeout(() => window.location.replace('/login'), 2000);
        return;
      }

      const token = localStorage.getItem('access_token');
      const authResponse = await fetch('/verify-auth', {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (!authResponse.ok) {
        throw new Error('Authentication failed');
      }

      const userData = await authResponse.json();

      if (!userData.user || userData.user.rol !== 'admin') {
        setAccessDenied(true);
        setLoading(false);
        return;
      }

      await loadDepartmentsAndRoles();
      setLoading(false);

    } catch (error) {
      console.error('Error loading form data:', error);
      
      // Fallback
      try {
        const token = localStorage.getItem('access_token');
        const pageResponse = await fetch('/register', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (pageResponse.ok) {
          const contentType = pageResponse.headers.get('content-type');
          if (contentType?.includes('text/html')) {
            window.location.reload();
            return;
          }
        }
      } catch (fallbackError) {
        console.error('Fallback failed:', fallbackError);
      }
      
      setAccessDenied(true);
      setLoading(false);
    }
  }, [checkAuth]);

  useEffect(() => {
    loadFormData();
  }, [loadFormData]);

  const loadDepartmentsAndRoles = async () => {
    // Datos hardcodeados como en el original
    const departmentsList = [
      { name: "Tecnología" },
      { name: "Recursos Humanos" },
      { name: "Ventas" },
      { name: "Marketing" },
      { name: "Administración" }
    ];
    
    const rolesList = ["admin", "user", "manager"];
    
    setDepartments(departmentsList);
    setRoles(rolesList);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const showError = (message: string) => {
    setError(message);
    setTimeout(() => setError(''), 5000);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError('');

    try {
      const token = localStorage.getItem('access_token');
      const formDataToSend = new FormData();
      
      Object.entries(formData).forEach(([key, value]) => {
        formDataToSend.append(key, value);
      });

      const response = await fetch('/register', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formDataToSend
      });

      if (response.ok) {
        alert('Usuario registrado exitosamente');
        setFormData({
          name: '',
          email: '',
          password: '',
          department_name: '',
          rol: ''
        });
      } else {
        const errorText = await response.text();
        showError(errorText || 'Error al registrar usuario');
      }

    } catch (error) {
      console.error('Error submitting form:', error);
      showError('Error de conexión. Por favor intenta nuevamente.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="auth-page">
        <div className="card">
          <h2>Crear cuenta</h2>
          <div style={{ textAlign: 'center', color: '#666' }}>
            Verificando permisos...
          </div>
        </div>
      </div>
    );
  }

  if (accessDenied) {
    return (
      <div className="auth-page">
        <div className="card">
          <h2>Crear cuenta</h2>
          <div style={{ display: 'block', textAlign: 'center' }}>
            <h3 style={{ color: '#d32f2f' }}>Acceso Denegado</h3>
            <p>No tienes permisos para acceder a esta página.</p>
            <p>Solo los administradores pueden registrar nuevos usuarios.</p>
            <a href="/dashboard">← Volver al Dashboard</a>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-page">
      <div className="card">
        <h2>Crear cuenta</h2>
        
        {error && (
          <div className="error" style={{ display: 'block' }}>
            {error}
          </div>
        )}
        
        <form onSubmit={handleSubmit}>
          <input
            id="name"
            name="name"
            placeholder="Nombre completo"
            value={formData.name}
            onChange={handleInputChange}
            required
          />
          
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
          
          <input
            list="departments-list"
            name="department_name"
            id="department_name"
            placeholder="Escribe el nombre del departamento"
            value={formData.department_name}
            onChange={handleInputChange}
          />
          <datalist id="departments-list">
            {departments.map((dept, index) => (
              <option key={index} value={dept.name} />
            ))}
          </datalist>
          
          <select
            name="rol"
            id="rol"
            value={formData.rol}
            onChange={handleInputChange}
            required
          >
            <option value="">Seleccionar rol</option>
            {roles.map((role, index) => (
              <option key={index} value={role}>
                {role.charAt(0).toUpperCase() + role.slice(1)}
              </option>
            ))}
          </select>
          
          <button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Registrando...' : 'Registrar'}
          </button>
        </form>
        
        <p style={{ marginTop: '10px' }}>
          <a href="/dashboard">← Volver al Dashboard</a>
        </p>
      </div>
    </div>
  );
};

export default Register;