# Importación de módulos necesarios para rutas, formularios, respuestas y autenticación
from fastapi import APIRouter, Request, Depends, Form, Response, HTTPException, status
from fastapi.templating import Jinja2Templates
from app.utils.db_operations import fetch_all
from app.controllers.userControllers import (
    register_user, authenticate_user, create_access_token,
    get_current_user, get_current_admin_user, revoke_token
)
from datetime import timedelta

# Inicialización del router y sistema de plantillas HTML
auth_router = APIRouter(tags=['auth'])

# Función auxiliar para obtener la lista de departamentos desde la base de datos
def _get_departments_list():
    try:
        rows = fetch_all("SELECT id, name FROM departments ORDER BY name")
        return rows or []
    except Exception:
        return []

# Función auxiliar para aplicar cabeceras de seguridad a las respuestas HTML
def _set_security_headers(response: Response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# Registro de usuario (POST) — protegido, solo administradores pueden registrar nuevos usuarios
@auth_router.post("/register")
def register(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    rol: str = Form(None),
    department_name: str | None = Form(None),
    current_admin=Depends(get_current_admin_user)
):
    try:
        user = register_user(name, email, password, rol, department_name)
        return {"message": "Usuario registrado exitosamente", "user": user}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Autenticación de usuario (POST) — pública, genera token JWT si las credenciales son válidas
@auth_router.post("/login")
def login(response: Response, request: Request, email: str = Form(...), password: str = Form(...)):
    user = authenticate_user(email, password)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    # Generación de token JWT con duración de 24 horas
    access_token_expires = timedelta(minutes=60 * 24)
    access_token = create_access_token(data={"sub": str(user["id"])}, expires_delta=access_token_expires)

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

# Verificación de autenticación (GET) — protegida, retorna datos del usuario autenticado
@auth_router.get("/verify-auth")
def verify_auth(current_user=Depends(get_current_user)):
    return {
        "authenticated": True,
        "user": {
            "id": current_user["id"],
            "name": current_user["name"],
            "email": current_user["email"],
            "rol": current_user["rol"]
        }
    }

@auth_router.get("/dashboard")
def dashboard(current_user=Depends(get_current_user)):
    return {
        "user": {
            "id": current_user["id"],
            "name": current_user["name"],
            "email": current_user["email"],
            "rol": current_user["rol"]
        }
    }

@auth_router.post("/logout")
def logout(request: Request):
    authorization = request.headers.get("Authorization")
    token = authorization.replace("Bearer ", "") if authorization and authorization.startswith("Bearer ") else None
    if token:
        revoke_token(token)  # tu lógica

    return {"message": "Logged out successfully"}

@auth_router.get("/users")
def users_list(current_admin=Depends(get_current_admin_user)):
    users = fetch_all("SELECT id, name, email, rol FROM users ORDER BY name")
    return {"users": users}

@auth_router.get("/register/data")
def get_register_data(current_admin=Depends(get_current_admin_user)):
    try:
        departments = _get_departments_list()
        return {
            "departments": departments,
            "available_roles": ["user", "admin"]  # o los roles que manejes
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading registration data: {str(e)}"
        )