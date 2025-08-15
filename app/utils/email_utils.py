# app/utils/email_utils.py
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