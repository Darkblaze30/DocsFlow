from fastapi import FastAPI
from routes.userRouters import router as auth_router
from fastapi.staticfiles import StaticFiles
from utils.db_operations import execute
from utils.db_connection import close_pool
import models.userModels as models_module

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
app.mount("/styles", StaticFiles(directory="app/styles"), name="styles")

@app.on_event("shutdown")
def shutdown():
    try:
        close_pool()
        print("🧹 Pool de conexiones cerrado correctamente.")
    except Exception:
        pass