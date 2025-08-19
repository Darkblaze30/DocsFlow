import React, { useEffect, useState } from "react";
import "./UnlockAccount.css";

const UnlockAccount: React.FC = () => {
  const [token, setToken] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [instruction, setInstruction] = useState(
    "Haz clic en el botón para desbloquear la cuenta del usuario."
  );
  const [loading, setLoading] = useState(false);
  const [buttonVisible, setButtonVisible] = useState(true);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const t = params.get("token");
    if (!t) {
      setMessage("Token no encontrado. Por favor, usa el enlace completo del correo.");
      setButtonVisible(false);
    } else {
      setToken(t);
    }
  }, []);

  const handleUnlock = async () => {
    if (!token) return;
    setLoading(true);
    setMessage("Procesando la solicitud...");

    try {
      const response = await fetch(`http://127.0.0.1:8000/auth/unlock-account?token=${token}`, {
        method: "GET",
      });

      const data = await response.json();

      if (response.ok) {
        setMessage(data.message || "Cuenta desbloqueada con éxito.");
        setInstruction("La cuenta ha sido desbloqueada.");
        setButtonVisible(false);
      } else {
        setMessage(data.detail || "Ha ocurrido un error al desbloquear la cuenta.");
      }
    } catch (error) {
      console.error("Error:", error);
      setMessage("No se pudo conectar con el servidor. Por favor, inténtalo más tarde.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="unlock-container">
      <div className="unlock-card">
        <h1 className="unlock-title">Desbloquear Cuenta</h1>
        <p className="unlock-subtitle">{instruction}</p>

        {message && <div className="unlock-message">{message}</div>}

        {buttonVisible && (
          <button
            onClick={handleUnlock}
            disabled={loading}
            className="unlock-button"
          >
            {loading ? "Desbloqueando..." : "Desbloquear Cuenta Ahora"}
          </button>
        )}
      </div>
    </div>
  );
};

export default UnlockAccount;
