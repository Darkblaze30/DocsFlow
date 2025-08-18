from fastapi import FastAPI , Query
from app.routes.userRouters import auth_router
from fastapi.staticfiles import StaticFiles
from app.utils.db_operations import execute
from app.utils.db_connection import close_pool
import app.models.userModels as models_module
from app.routes.document_route import router as document_router
from app.routes.auth import router as auth_router_email
from app.controllers.auth_controller import unlock_account_handler
app = FastAPI()

@app.on_event("startup")
def startup():
    print("🚀 Startup: asegurando tablas (dev)...")
    try:
        for sql in models_module.get_create_table_statements():
            try:
                execute(sql)
            except Exception as e:
                print("⚠️ Aviso creando tabla:", e)
        print("✅ Intento de creación de tablas completado.")
    except Exception as e:
        print("❌ No se pudieron ejecutar los DDLs de creación de tablas. Revisa la conexión a la BD:", e)
app.include_router(auth_router)
app.include_router(document_router, prefix="/api/documents")
app.include_router(auth_router_email)

app.mount("/styles", StaticFiles(directory="app/styles"), name="styles")

@auth_router_email.get("/unlock-account", status_code=200)
def unlock_account(token: str = Query(...)):
    """Endpoint para que un administrador desbloquee una cuenta de usuario."""
    return unlock_account_handler(token)

@app.on_event("shutdown")
def shutdown():
    try:
        close_pool()
        print("🧹 Pool de conexiones cerrado correctamente.")
    except Exception:
        pass