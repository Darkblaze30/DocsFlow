from .db_connection import get_conn
import mysql.connector
from dotenv import load_dotenv
import os

def get_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        database=os.getenv("DB_NAME")
    )

def fetch_one(query: str, params: tuple | dict | None = None):
    with get_conn() as conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            row = cursor.fetchone()
            return row
        finally:
            cursor.close()

def fetch_all(query: str, params: tuple | dict | None = None):
    with get_conn() as conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            rows = cursor.fetchall()
            return rows
        finally:
            cursor.close()

def execute(query: str, params: tuple | dict | None = None):
    with get_conn() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(query, params or ())
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            conn.rollback()
            raise
        finally:
            cursor.close()

def execute_query(query: str, params: tuple = None, fetch_one: bool = False, fetch_all: bool = False):
    """
    Ejecuta una consulta SQL y maneja los resultados y errores.
    
    Retorna los resultados de la consulta o un booleano para operaciones de escritura.
    """
    conn = None
    cursor = None
    try:
        conn = get_db()
        if conn is None:
            # Si no hay conexión, retorna None o False
            return None
            
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params)
        
        # Lógica para manejar SELECT, INSERT, UPDATE, DELETE
        if query.strip().lower().startswith("select"):
            if fetch_one:
                return cursor.fetchone()
            if fetch_all:
                return cursor.fetchall()
        else:
            conn.commit()
            return True
            
    except mysql.connector.Error as err:
        print(f"Error en la base de datos al ejecutar la consulta: {err}")
        if conn:
            conn.rollback()
        return False
    finally:
        # Asegúrate de que el cursor y la conexión se cierren, incluso si hay un error
        if cursor:
            cursor.close()
        if conn:
            conn.close()