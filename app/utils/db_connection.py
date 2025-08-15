import os
from dotenv import load_dotenv
from mysql.connector.pooling import MySQLConnectionPool
from mysql.connector import Error
from contextlib import contextmanager

load_dotenv()

DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "password")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_NAME = os.getenv("DB_NAME", "login_db")
POOL_NAME = os.getenv("DB_POOL_NAME", "app_pool")
POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "5"))

_pool: MySQLConnectionPool | None = None

def _ensure_pool():
    global _pool
    if _pool is None:
        try:
            _pool = MySQLConnectionPool(
                pool_name=POOL_NAME,
                pool_size=POOL_SIZE,
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASS,
                database=DB_NAME,
                autocommit=False,
            )
        except Error as e:
            raise RuntimeError(f"Error creando el pool de conexiones: {e}")

@contextmanager
def get_conn():
    _ensure_pool()
    conn = _pool.get_connection()
    try:
        yield conn
    finally:
        try:
            if conn.is_connected():
                conn.close()
        except Exception:
            pass

def close_pool():
    global _pool
    if _pool is not None:
        try:
            _pool = None
        finally:
            _pool = None