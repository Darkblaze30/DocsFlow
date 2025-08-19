import React, { useState, useEffect } from "react";
import "./ResetPassword.css";

const ResetPassword: React.FC = () => {
  const [password, setPassword] = useState("");
  const [passwordConfirm, setPasswordConfirm] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [messageType, setMessageType] = useState<"success" | "error" | "info" | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [formVisible, setFormVisible] = useState(true);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const t = params.get("token");
    if (!t) {
      setMessage("Token no encontrado. Por favor, usa el enlace completo del correo.");
      setMessageType("error");
      setFormVisible(false);
    } else {
      setToken(t);
    }
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (password !== passwordConfirm) {
      setMessage("Las contraseñas no coinciden.");
      setMessageType("error");
      return;
    }

    setMessage("Restableciendo contraseña...");
    setMessageType("info");

    try {
      const response = await fetch("http://127.0.0.1:8000/auth/reset-password", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ token, password, passwordConfirm }),
      });

      const data = await response.json();

      if (response.ok) {
        setMessage("Contraseña restablecida con éxito. ¡Ya puedes iniciar sesión!");
        setMessageType("success");
        setFormVisible(false);
      } else {
        setMessage(data.detail || "Ha ocurrido un error al restablecer la contraseña.");
        setMessageType("error");
      }
    } catch (error) {
      console.error("Error:", error);
      setMessage("No se pudo conectar con el servidor. Por favor, inténtalo de nuevo más tarde.");
      setMessageType("error");
    }
  };

  return (
    <div className="reset-container">
      <div className="reset-card">
        <h1 className="reset-title">Restablecer Contraseña</h1>
        <p className="reset-subtitle">Ingresa tu nueva contraseña para acceder a tu cuenta.</p>

        {formVisible && (
          <form onSubmit={handleSubmit} className="reset-form">
            <div>
              <label className="reset-label">Nueva Contraseña</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="reset-input"
              />
            </div>
            <div>
              <label className="reset-label">Confirmar Contraseña</label>
              <input
                type="password"
                value={passwordConfirm}
                onChange={(e) => setPasswordConfirm(e.target.value)}
                required
                className="reset-input"
              />
            </div>

            <button type="submit" className="reset-button">
              Restablecer Contraseña
            </button>
          </form>
        )}

        {message && (
          <div
            className={`reset-message ${
              messageType === "success"
                ? "reset-success"
                : messageType === "error"
                ? "reset-error"
                : "reset-info"
            }`}
          >
            {message}
          </div>
        )}
      </div>
    </div>
  );
};

export default ResetPassword;
