from fastapi import APIRouter, Request, Depends, Form, Response
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from utils.db_operations import fetch_all
from controllers.userControllers import register_user, authenticate_user, create_access_token, get_current_user
from datetime import timedelta
from controllers.userControllers import get_current_admin_user

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def _get_departments_list():
    try:
        rows = fetch_all("SELECT id, name FROM departments ORDER BY name")
        return rows or []
    except Exception:
        return []


@router.get("/register")
def register_page(request: Request, current_admin=Depends(get_current_admin_user)):
    from models.userModels import RoleEnum
    roles = [role.value for role in RoleEnum]
    departments = _get_departments_list()
    return templates.TemplateResponse("register.html", {
        "request": request,
        "roles": roles,
        "departments": departments
    })


@router.post("/register")
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
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": str(e),
            "roles": roles,
            "departments": departments,
            "form": {"name": name, "email": email, "department_name": department_name}
        })
    return RedirectResponse("/login", status_code=303)


@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
def login(response: Response, request: Request, email: str = Form(...), password: str = Form(...)):
    user = authenticate_user(email, password)
    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Credenciales inválidas"})
    access_token_expires = timedelta(minutes=60 * 24)
    access_token = create_access_token(data={"sub": str(user["id"])}, expires_delta=access_token_expires)
    response = RedirectResponse("/dashboard", status_code=303)
    response.set_cookie(key="access_token", value=access_token, httponly=True, samesite="lax")
    return response


@router.get("/dashboard")
def dashboard(request: Request, current_user=Depends(get_current_user)):
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": current_user})


@router.get("/logout")
def logout(response: Response):
    response = RedirectResponse("/login", status_code=303)
    response.delete_cookie("access_token")
    return response

@router.get("/users")
def users_list(request: Request, current_admin=Depends(get_current_admin_user)):
    # Mostrar lista de todos los usuarios (solo admins)
    pass

@router.get("/departments") 
def departments_list(request: Request, current_admin=Depends(get_current_admin_user)):
    # Gestionar departamentos (solo admins)
    pass