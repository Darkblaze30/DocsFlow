from app.models.password_reset import PasswordResetRequest, PasswordResetConfirm, User
from app.utils.email_utils import send_password_reset_email
from app.database import execute_query
import uuid
import bcrypt
from datetime import datetime, timedelta
from typing import Optional

#def get_user_by_email(email: str) -> Optional[User]:
 #   query = "SELECT id, email, password, role FROM users WHERE email = %s"
  #  user_data = execute_query(query, (email,), fetch_one=True)
   # return User(**user_data) if user_data else None
def get_user_by_email(email: str) -> Optional[User]:
    """Busca un usuario por su email en la base de datos, incluyendo su rol."""
    # Corrige la consulta SELECT para que incluya la columna 'role'
    query = "SELECT id, email, password, role FROM users WHERE email = %s"
    user_data = execute_query(query, (email,), fetch_one=True)
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
    query = "SELECT user_id, expires_at, token_hash FROM password_resets WHERE token_hash = %s"
    token_record = execute_query(query, (token,), fetch_one=True)
    return token_record

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

#async def reset_password_handler(request: PasswordResetConfirm):
 #   token_record = get_reset_token_record(request.token)
    
  #  if not token_record or token_record['expires_at'] < datetime.now():
   #     return {"message": "Token inválido o expirado. Por favor, solicita uno nuevo."}

    #if request.new_password != request.confirm_password:
     #   return {"message": "Las contraseñas no coinciden."}
        
    #new_password_hash = bcrypt.hashpw(request.new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
   # update_user_password(token_record['user_id'], new_password_hash)
    #delete_reset_token_record(token_record['token_hash'])

#    return {"message": "Contraseña actualizada con éxito."}


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
