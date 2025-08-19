// src/hooks/useInactivity.ts
import { useState, useEffect, useCallback, useRef } from 'react';

const INACTIVITY_TIME = 28 * 60 * 1000; // 28 minutos
const WARNING_TIME = 2 * 60 * 1000; // 2 minutos

const activityEvents = [
  'mousedown', 'mousemove', 'keypress', 'scroll',
  'touchstart', 'click', 'keydown'
];

export const useInactivity = () => {
  const [showModal, setShowModal] = useState(false);
  const [countdown, setCountdown] = useState('02:00');
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  
  const inactivityTimer = useRef<number>(0);
  const warningTimer = useRef<number>(0);
  const countdownTimer = useRef<number>(0);
  const countdownSeconds = useRef(120);

  const performLogout = useCallback(async (isAutomatic = false) => {
    if (isLoggingOut) return;

    setIsLoggingOut(true);

    // Limpiar todos los timers
    if (inactivityTimer.current) clearTimeout(inactivityTimer.current);
    if (warningTimer.current) clearTimeout(warningTimer.current);
    if (countdownTimer.current) clearInterval(countdownTimer.current);

    // Remover event listeners
    activityEvents.forEach(event => {
      document.removeEventListener(event, resetInactivityTimer, true);
    });

    // Llamar logout en el servidor
    const token = localStorage.getItem('access_token');
    if (token) {
      try {
        await fetch('/logout', {
          method: 'GET',
          headers: { 'Authorization': `Bearer ${token}` }
        });
      } catch (error) {
        console.error('Error during logout:', error);
      }
    }

    // Limpiar storage
    localStorage.clear();
    sessionStorage.clear();

    if (isAutomatic) {
      alert('Tu sesión ha expirado por inactividad. Serás redirigido al login.');
    }

    setTimeout(() => {
      window.location.replace('/login');
    }, 1000);
  }, []);

  const updateCountdown = useCallback(() => {
    const minutes = Math.floor(countdownSeconds.current / 60);
    const seconds = countdownSeconds.current % 60;
    const display = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    setCountdown(display);

    if (countdownSeconds.current <= 0) {
      performLogout(true);
      return;
    }
    countdownSeconds.current--;
  }, [performLogout]);

  const showInactivityWarning = useCallback(() => {
    setShowModal(true);
    countdownSeconds.current = 120;
    updateCountdown();
    
    countdownTimer.current = setInterval(updateCountdown, 1000);
    warningTimer.current = setTimeout(() => {
      performLogout(true);
    }, WARNING_TIME);
  }, [updateCountdown, performLogout]);

  const resetInactivityTimer = useCallback(() => {
    // Limpiar timers existentes
    if (inactivityTimer.current) clearTimeout(inactivityTimer.current);
    if (warningTimer.current) clearTimeout(warningTimer.current);
    if (countdownTimer.current) clearInterval(countdownTimer.current);

    // Ocultar modal y resetear countdown
    setShowModal(false);
    countdownSeconds.current = 120;

    // Configurar nuevo timer de inactividad
    inactivityTimer.current = setTimeout(() => {
      showInactivityWarning();
    }, INACTIVITY_TIME);
  }, [showInactivityWarning]);

  const extendSession = useCallback(() => {
    setShowModal(false);
    if (warningTimer.current) clearTimeout(warningTimer.current);
    if (countdownTimer.current) clearInterval(countdownTimer.current);
    resetInactivityTimer();
  }, [resetInactivityTimer]);

  const setupActivityListeners = useCallback(() => {
    activityEvents.forEach(event => {
      document.addEventListener(event, resetInactivityTimer, true);
    });
  }, [resetInactivityTimer]);

  // Configurar listeners y timer inicial
  useEffect(() => {
    setupActivityListeners();
    resetInactivityTimer();

    // Cleanup al desmontar
    return () => {
      if (inactivityTimer.current) clearTimeout(inactivityTimer.current);
      if (warningTimer.current) clearTimeout(warningTimer.current);
      if (countdownTimer.current) clearInterval(countdownTimer.current);
      
      activityEvents.forEach(event => {
        document.removeEventListener(event, resetInactivityTimer, true);
      });
    };
  }, [setupActivityListeners, resetInactivityTimer]);

  // Manejar eventos de navegación
  useEffect(() => {
    const handlePageShow = (event: PageTransitionEvent) => {
      if (event.persisted) {
        window.location.reload();
      }
    };

    const handlePopState = () => {
      if (!isLoggingOut) {
        const currentPath = window.location.pathname;
        if (currentPath === '/login' || currentPath === '/' || !currentPath.startsWith('/dashboard')) {
          localStorage.clear();
          sessionStorage.clear();
          window.location.replace('/login');
        }
      }
    };

    const handleBeforeUnload = (event: BeforeUnloadEvent) => {
      if (!isLoggingOut) {
        const destination = (event.target as any)?.activeElement;
        if (destination?.tagName === 'A') {
          const href = destination.href;
          if (href && (href.includes('/register') || href.includes('/users') || href.includes('/departments'))) {
            return;
          }
        }
        event.preventDefault();
        return event.returnValue = '¿Estás seguro de que deseas salir?';
      }
    };

    window.addEventListener('pageshow', handlePageShow);
    window.addEventListener('popstate', handlePopState);
    window.addEventListener('beforeunload', handleBeforeUnload);

    return () => {
      window.removeEventListener('pageshow', handlePageShow);
      window.removeEventListener('popstate', handlePopState);
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, [isLoggingOut]);

  return {
    showModal,
    countdown,
    extendSession,
    isLoggingOut,
    performLogout
  };
};