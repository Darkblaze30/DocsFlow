// src/components/Dashboard/Dashboard.tsx
import React, { useState, useEffect } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { useInactivity } from '../../hooks/useInactivity';
import { getDashboardData } from '../../services/authService';
import InactivityModal from '../InactivityModal/inactivityModal';
import { Link, Navigate } from 'react-router-dom';
import type { User } from '../../types/auth';
import './dashboard.css';

const Dashboard: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const { logout, checkAuth, verifyToken } = useAuth();
  const { showModal, countdown, extendSession, isLoggingOut } = useInactivity();

  useEffect(() => {
    const loadUserData = async () => {
      try {
        // Verificar autenticación primero
        if (!checkAuth()) {
          setIsAuthenticated(false);
          setLoading(false);
          return;
        }

        const tokenValid = await verifyToken();
        if (!tokenValid) {
          setIsAuthenticated(false);
          setLoading(false);
          return;
        }

        const dashboardData = await getDashboardData();
        setUser(dashboardData.user);
        setIsAuthenticated(true);
      } catch (error) {
        console.error('Error loading user data:', error);
        setIsAuthenticated(false);
      } finally {
        setLoading(false);
      }
    };

    loadUserData();
  }, [checkAuth, verifyToken]);

  const handleLogout = async () => {
    if (confirm('¿Estás seguro de que deseas cerrar sesión?')) {
      await logout();
    }
  };

  // Mostrar loading
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

  // Redirigir al login si no está autenticado
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return (
    <>
      <div className="box">
        <h1>
          Bienvenido, <span>{user?.name || 'Sin nombre'}</span> 🌟
        </h1>

        <div className="user-info">
          <p>
            <strong>Correo:</strong>
            <span>{user?.email || 'Sin email'}</span>
          </p>
          <p>
            <strong>Rol:</strong>
            <span className={`role-badge role-${user?.rol || 'user'}`}>
              {(user?.rol || 'user').toUpperCase()}
            </span>
          </p>
        </div>

        <div className="actions">
          <button
            onClick={handleLogout}
            disabled={isLoggingOut}
            style={{
              pointerEvents: isLoggingOut ? 'none' : 'auto'
            }}
          >
            {isLoggingOut ? 'Cerrando sesión...' : 'Cerrar sesión'}
          </button>
        </div>

        {user?.rol === 'admin' && (
          <div className="admin-visible">
            <h3>🔧 Panel de Administrador</h3>
            <div className="actions">
              <Link to="/register">👤 Registrar Usuarios</Link>
              <Link to="/users">📋 Ver Todos los Usuarios</Link>
            </div>
          </div>
        )}
      </div>

      <InactivityModal
        show={showModal}
        countdown={countdown}
        onExtend={extendSession}
        onLogout={logout}
      />
    </>
  );
};

export default Dashboard;