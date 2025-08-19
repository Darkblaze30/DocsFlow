// src/components/InactivityModal/InactivityModal.tsx
import React, { useEffect } from 'react';
import './inactivityModal.css';

interface InactivityModalProps {
  show: boolean;
  countdown: string;
  onExtend: () => void;
  onLogout: () => void;
}

const InactivityModal: React.FC<InactivityModalProps> = ({
  show,
  countdown,
  onExtend,
  onLogout
}) => {
  useEffect(() => {
    const handleEscapeKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && show) {
        onExtend();
      }
    };

    document.addEventListener('keydown', handleEscapeKey);
    return () => document.removeEventListener('keydown', handleEscapeKey);
  }, [show, onExtend]);

  if (!show) return null;

  return (
    <div className="inactivity-modal" style={{ display: 'block' }}>
      <div className="inactivity-content">
        <h2>⏰ Sesión por Expirar</h2>
        <p>Has estado inactivo por mucho tiempo.</p>
        <p>Tu sesión expirará en:</p>
        <div className="countdown">{countdown}</div>
        <p><small>¿Deseas continuar trabajando?</small></p>
        <div className="modal-buttons">
          <button className="btn-extend" onClick={onExtend}>
            Continuar Sesión
          </button>
          <button className="btn-logout" onClick={onLogout}>
            Cerrar Sesión
          </button>
        </div>
      </div>
    </div>
  );
};

export default InactivityModal;