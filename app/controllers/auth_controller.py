from app.models.password_reset import PasswordResetRequest, PasswordResetConfirm, User
from app.utils.email_utils import send_password_reset_email,send_account_locked_email_to_admin
from app.utils.db_operations import execute_query
import uuid
import bcrypt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException

def get_user_by_email(email: str) -> Optional[User]:
    query = "SELECT id, email, password, rol, failed_attempts, is_locked FROM users WHERE email = %s"
    user_data = execute_query(query, (email,), fetch_one=True)
    return User(**user_data) if user_data else None

def get_user_by_id(user_id: int) -> Optional[User]:
    query = "SELECT id, email, password, rol, failed_attempts, is_locked FROM users WHERE id = %s"
    user_data = execute_query(query, (user_id,), fetch_one=True)
    return User(**user_data) if user_data else None

def update_user_password(user_id: int, new_password_hash: str):
    query = "UPDATE users SET password = %s WHERE id = %s"
    execute_query(query, (new_password_hash, user_id))

def save_reset_token(user_id: int, token: str):
    hashed_token = bcrypt.hashpw(token.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    expires_at = datetime.now() + timedelta(hours=1)
    
    query = "INSERT INTO password_resets (user_id, token_hash, expires_at) VALUES (%s, %s, %s)"
    execute_query(query, (user_id, hashed_token, expires_at))

def get_reset_token_record(token: str):
    query = "SELECT user_id, expires_at, token_hash FROM password_resets"
    records = execute_query(query, fetch_all=True)

    for record in records:
        if bcrypt.checkpw(token.encode('utf-8'), record['token_hash'].encode('utf-8')):
            return record

    return None 


def delete_reset_token_record(token_hash: str):
    query = "DELETE FROM password_resets WHERE token_hash = %s"
    execute_query(query, (token_hash,))

async def forgot_password_handler(request: PasswordResetRequest):
    user = get_user_by_email(request.email)
    if user:
        token = str(uuid.uuid4())
        await send_password_reset_email(request.email, token)
        save_reset_token(user.id, token)

    return {"message": "Si el correo electrónico existe, se ha enviado un enlace para restablecer la contraseña."}



async def forgot_password_handler(request: PasswordResetRequest):
    print("DEBUG: forgot_password_handler - Petición recibida.")
    user = get_user_by_email(request.email)
    print(f"DEBUG: forgot_password_handler - Usuario encontrado: {user is not None}")
    if user:
        token = str(uuid.uuid4())
        print("DEBUG: forgot_password_handler - Token generado. Intentando enviar email...")
        try:
            await send_password_reset_email(request.email, token)
            print("DEBUG: forgot_password_handler - Email enviado con éxito (o sin errores).")
        except Exception as e:
            print(f"ERROR: No se pudo enviar el email. Detalles: {e}")

        save_reset_token(user.id, token)
        print("DEBUG: forgot_password_handler - Token guardado en BD.")

    print("DEBUG: forgot_password_handler - Finalizando petición.")
    return {"message": "Si el correo electrónico existe, se ha enviado un enlace para restablecer la contraseña."}


async def reset_password_handler(request: PasswordResetConfirm):
    token_record = get_reset_token_record(request.token)
    print(request.token)
    if not token_record or token_record['expires_at'] < datetime.now():
        return {"message": "Token inválido o expirado. Por favor, solicita uno nuevo."}

    if request.new_password != request.confirm_password:
        return {"message": "Las contraseñas no coinciden."}

    new_password_hash = bcrypt.hashpw(request.new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    update_user_password(token_record['user_id'], new_password_hash)
    delete_reset_token_record(token_record['token_hash'])

    return {"message": "Contraseña actualizada con éxito."}


async def login_for_access_token_handler(email: str, password: str):
    user = get_user_by_email(email)

    if not user:
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos")

    # Verifica si la cuenta está bloqueada
    if user.is_locked:
        raise HTTPException(status_code=403, detail="Tu cuenta está bloqueada debido a demasiados intentos fallidos. Un administrador ha sido notificado.")

    # Verifica si la contraseña es correcta
    if not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        # Contraseña incorrecta, incrementa el contador de intentos
        new_attempts = user.failed_attempts + 1
        query = "UPDATE users SET failed_attempts = %s WHERE id = %s"
        execute_query(query, (new_attempts, user.id))

        if new_attempts >= 5:
            # Bloquea la cuenta
            query = "UPDATE users SET is_locked = TRUE WHERE id = %s"
            execute_query(query, (user.id,))
            
            # Envía un correo al administrador con un token de desbloqueo (el ID del usuario)
            await send_account_locked_email_to_admin(user.email, str(user.id))
            
            raise HTTPException(
                status_code=403,
                detail="Demasiados intentos de login fallidos. La cuenta ha sido bloqueada. Un administrador ha sido notificado."
            )
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos")

    # Si la contraseña es correcta, reinicia los intentos fallidos
    if user.failed_attempts > 0:
        query = "UPDATE users SET failed_attempts = 0 WHERE id = %s"
        execute_query(query, (user.id,))

    # Aquí iría la lógica para generar el JWT, que ya tienes
    # ...
    return {"message": "Login exitoso.."} # Placeholder


def unlock_account_handler(token: str):
    try:
        user_id = int(token)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Token de desbloqueo inválido.")

    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    # Si la cuenta está bloqueada, la desbloquea y reinicia los intentos
    if user.is_locked:
        query = "UPDATE users SET is_locked = FALSE, failed_attempts = 0 WHERE id = %s"
        execute_query(query, (user_id,))
        return {"message": f"Cuenta de {user.email} desbloqueada con éxito."}
    else:
        return {"message": "La cuenta no estaba bloqueada."}
