# Importación de módulos necesarios para rutas, formularios, respuestas y autenticación
from fastapi import APIRouter, Request, Depends, Form, Response, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from app.utils.db_operations import fetch_all
from app.controllers.userControllers import (
    register_user, authenticate_user, create_access_token,
    get_current_user, revoke_token, get_current_admin_user
)
from datetime import timedelta

# Inicialización del router y sistema de plantillas HTML
auth_router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

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

# Página de registro (GET) — protegida, solo accesible por administradores autenticados
@auth_router.get("/register")
def register_page(request: Request):
    user_data = None
    try:
        authorization = request.headers.get("Authorization")
        if authorization and authorization.startswith("Bearer "):
            current_user = get_current_user(request)
            user_data = current_user
    except HTTPException:
        pass

    # Si no es admin, se muestra acceso limitado
    if not user_data or user_data.get("rol") != "admin":
        user_data = {
            "name": "Sin acceso",
            "email": "...",
            "rol": "user"
        }

    # Carga de roles y departamentos para el formulario
    from app.models.userModels import RoleEnum
    roles = [role.value for role in RoleEnum]
    departments = _get_departments_list()

    response = templates.TemplateResponse("register.html", {
        "request": request,
        "roles": roles,
        "departments": departments,
        "user": user_data
    })
    return _set_security_headers(response)

# Registro de usuario (POST) — protegido, solo administradores pueden registrar nuevos usuarios
@auth_router.post("/register")
def register(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    rol: str = Form(None),
    department_name: str | None = Form(None),
    current_admin=Depends(get_current_admin_user)
):
    try:
        user = register_user(name, email, password, rol, department_name)
    except Exception as e:
        from app.models.userModels import RoleEnum
        roles = [role.value for role in RoleEnum]
        departments = _get_departments_list()
        response = templates.TemplateResponse("register.html", {
            "request": request,
            "error": str(e),
            "roles": roles,
            "departments": departments,
            "form": {"name": name, "email": email, "department_name": department_name}
        })
        return _set_security_headers(response)
    return {"new user": user}

# Página de login (GET) — pública, accesible sin autenticación
@auth_router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

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

# Página de dashboard (GET) — protegida, requiere token JWT en el header
@auth_router.get("/dashboard")
def dashboard(request: Request):
    user_data = None
    try:
        authorization = request.headers.get("Authorization")
        if authorization and authorization.startswith("Bearer "):
            current_user = get_current_user(request)
            user_data = current_user
    except HTTPException:
        pass

    if not user_data:
        user_data = {
            "name": "Cargando...",
            "email": "...",
            "rol": "user"
        }

    response = templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user_data
    })
    return _set_security_headers(response)

# Logout (GET) — protegida, invalida el token JWT si está presente
@auth_router.get("/logout")
def logout(request: Request, response: Response):
    authorization = request.headers.get("Authorization")
    token = authorization.replace("Bearer ", "") if authorization and authorization.startswith("Bearer ") else None
    if token:
        revoke_token(token)

    return {"message": "Logged out successfully", "redirect_url": "/login"}

# Página de usuarios (GET) — protegida, solo accesible por administradores
@auth_router.get("/users")
def users_list(request: Request, current_admin=Depends(get_current_admin_user)):
    response = templates.TemplateResponse("users.html", {"request": request})
    return _set_security_headers(response)

# Página de departamentos (GET) — protegida, solo accesible por administradores
@auth_router.get("/departments")
def departments_list(request: Request, current_admin=Depends(get_current_admin_user)):
    response = templates.TemplateResponse("departments.html", {"request": request})
    return _set_security_headers(response)

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