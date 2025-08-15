from .db_connection import get_conn

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