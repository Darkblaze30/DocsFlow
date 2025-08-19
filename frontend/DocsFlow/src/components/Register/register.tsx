// src/components/Register/Register.tsx
import React, { useState, useEffect } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { getRegisterFormData, registerUser } from '../../services/authService';
import { Navigate, Link } from 'react-router-dom';
import type { RegisterFormData, Department } from '../../types/auth';
import './Register.css';

const Register: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [roles, setRoles] = useState<string[]>([]);
  const { checkAuth, verifyToken,  } = useAuth();

  const [formData, setFormData] = useState<RegisterFormData>({
    name: '',
    email: '',
    password: '',
    department_name: '',
    rol: ''
  });

  useEffect(() => {
    const initializeForm = async () => {
      try {
        // Verificar autenticación básica
        if (!checkAuth()) {
          setIsAuthenticated(false);
          setLoading(false);
          return;
        }

        // Verificar token con el backend
        const tokenValid = await verifyToken();
        if (!tokenValid) {
          setIsAuthenticated(false);
          setLoading(false);
          return;
        }

        setIsAuthenticated(true);

        // Intentar obtener datos del formulario (esto fallará si no es admin)
        try {
          const data = await getRegisterFormData();
          setDepartments(data.departments);
          setRoles(data.available_roles);
          setIsAdmin(true);
        } catch (err) {
          console.log(err)
          setIsAdmin(false);
        }
      } catch (error) {
        console.error('Error loading form data:', error);
        setIsAuthenticated(false);
      } finally {
        setLoading(false);
      }
    };

    initializeForm();
  }, [checkAuth, verifyToken]);

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
      const formDataToSend = new FormData();
      Object.entries(formData).forEach(([key, value]) => {
        formDataToSend.append(key, value);
      });

      await registerUser(formDataToSend);
      alert('Usuario registrado exitosamente');
      setFormData({
        name: '',
        email: '',
        password: '',
        department_name: '',
        rol: ''
      });
    } catch (error: any) {
      showError(error.message || 'Error al registrar usuario');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Mostrar loading
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

  // Redirigir al login si no está autenticado
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Mostrar acceso denegado si no es admin
  if (!isAdmin) {
    return (
      <div className="auth-page">
        <div className="card">
          <h2>Crear cuenta</h2>
          <div style={{ textAlign: 'center' }}>
            <h3 style={{ color: '#d32f2f' }}>Acceso Denegado</h3>
            <p>Solo los administradores pueden registrar nuevos usuarios.</p>
            <Link to="/dashboard">← Volver al Dashboard</Link>
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
            name="name"
            placeholder="Nombre completo"
            value={formData.name}
            onChange={handleInputChange}
            required
          />
          
          <input
            name="email"
            placeholder="Correo electrónico"
            type="email"
            value={formData.email}
            onChange={handleInputChange}
            required
          />
          
          <input
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
          <Link to="/dashboard">← Volver al Dashboard</Link>
        </p>
      </div>
    </div>
  );
};

export default Register;