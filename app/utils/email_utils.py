from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from dotenv import load_dotenv
import os

load_dotenv()

print("DEBUG: email_utils.py - Cargando configuración de correo.")

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_USERNAME"),
    MAIL_PORT=int(os.getenv("MAIL_PORT")),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_FROM_NAME=os.getenv("MAIL_FROM_NAME"),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

async def send_password_reset_email(email: str, token: str):
    print(f"DEBUG: send_password_reset_email - Intentando enviar a {email} con token {token}.")
    frontend_url = os.getenv("FRONTEND_URL")
    reset_url = f"{frontend_url}/reset-password?token={token}"
    html_body = f"""
    <p>Hola,</p>
    <p>Hemos recibido una solicitud para restablecer tu contraseña. Haz clic en el siguiente enlace para continuar:</p>
    <a href="{reset_url}">Restablecer Contraseña</a>
    <p>Si no solicitaste este cambio, puedes ignorar este correo.</p>
    <p>El equipo de DocsFlow</p>
    """
    message = MessageSchema(
        subject="Recuperación de Contraseña - DocsFlow",
        recipients=[email],
        body=html_body,
        subtype="html"
    )
    fm = FastMail(conf)
    print("DEBUG: send_password_reset_email - FastMail configurado. Enviando mensaje.")
    await fm.send_message(message)
    print("DEBUG: send_password_reset_email - Mensaje enviado (o la llamada fue exitosa).")
    
    
    async def send_account_locked_email_to_admin(user_email: str, unlock_token: str):
    admin_email = os.getenv("ADMIN_EMAIL")
    if not admin_email:
        print("ERROR: No se pudo enviar el correo de notificación. La variable ADMIN_EMAIL no está configurada.")
        return

    unlock_url = f"http://127.0.0.1:8000/auth/unlock-account?token={unlock_token}"
    
    html_body = f"""
    <p>¡Alerta de seguridad!</p>
    <p>El usuario <strong>{user_email}</strong> ha sido bloqueado por exceder el número de intentos de login fallidos.</p>
    <p>Para desbloquear su cuenta de inmediato, haz clic en el siguiente enlace:</p>
    <a href="{unlock_url}">Desbloquear Cuenta</a>
    <p>Este es un enlace único y solo debe ser usado por un administrador.</p>
    <p>El equipo de DocsFlow</p>
    """
    message = MessageSchema(
        subject=f"Alerta: Cuenta de {user_email} ha sido bloqueada",
        recipients=[admin_email],
        body=html_body,
        subtype="html"
    )
    
    fm = FastMail(conf)
    await fm.send_message(message)
    print("DEBUG: Correo de notificación de bloqueo enviado al administrador.")