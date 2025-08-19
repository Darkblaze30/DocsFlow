// src/components/Dashboard/Dashboard.tsx
import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { useInactivity } from '../../hooks/useInactivity';
import InactivityModal from '../InactivityModal/inactivityModal';
import type { User } from '../../types/auth';
import './dashboard.css';

const Dashboard: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const { logout } = useAuth();
  const { showModal, countdown, extendSession, isLoggingOut } = useInactivity();

  const loadUserData = useCallback(async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        window.location.replace('/login');
        return;
      }

      // Intentar verify-auth primero
      let response = await fetch('/verify-auth', {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setUser(data.user);
        setLoading(false);
        return;
      }

      // Fallback a dashboard
      response = await fetch('/dashboard', {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const contentType = response.headers.get('content-type');
        if (contentType?.includes('application/json')) {
          const data = await response.json();
          setUser(data.user);
        } else {
          // Si es HTML, extraer datos del template
          setUser(null); // Manejar según tu lógica
        }
      } else {
        throw new Error('Authentication failed');
      }
    } catch (error) {
      console.error('Error loading user data:', error);
      setTimeout(() => window.location.replace('/login'), 3000);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadUserData();
  }, [loadUserData]);

  const handleLogout = async () => {
    const confirmLogout = confirm('¿Estás seguro de que deseas cerrar sesión?');
    if (confirmLogout) {
      await logout();
    }
  };

  if (loading) {
    return (
      <div className="box">
        <h1>Bienvenido, <span>Cargando...</span> 🌟</h1>
        <div className="user-info">
          <p><strong>Correo:</strong> <span>...</span></p>
          <p><strong>Rol:</strong> <span className="role-badge role-user">...</span></p>
        </div>
      </div>
    );
  }

  return (
    <>
      <div className="box">
        <h1>
          Bienvenido, <span id="userName">{user?.name || 'Sin nombre'}</span> 🌟
        </h1>
        
        <div className="user-info">
          <p>
            <strong>Correo:</strong> 
            <span id="userEmail">{user?.email || 'Sin email'}</span>
          </p>
          <p>
            <strong>Rol:</strong>
            <span className={`role-badge role-${user?.rol || 'user'}`} id="userRoleSpan">
              <span id="userRoleText">{(user?.rol || 'user').toUpperCase()}</span>
            </span>
          </p>
        </div>

        <div className="actions">
          <a 
            href="#" 
            onClick={handleLogout} 
            id="logout-btn"
            style={{ 
              pointerEvents: isLoggingOut ? 'none' : 'auto'
            }}
          >
            {isLoggingOut ? 'Cerrando sesión...' : 'Cerrar sesión'}
          </a>
        </div>

        {user?.rol === 'admin' && (
          <div id="adminPanel" className="admin-visible">
            <h3>🔧 Panel de Administrador</h3>
            <div className="actions">
              <a href="/register">👤 Registrar Usuarios</a>
              <a href="/users">📋 Ver Todos los Usuarios</a>
              <a href="/departments">🏢 Gestionar Departamentos</a>
            </div>
          </div>
        )}
      </div>

      <InactivityModal 
        show={showModal}
        countdown={countdown}
        onExtend={extendSession}
        onLogout={() => logout(true)}
      />
    </>
  );
};

export default Dashboard;