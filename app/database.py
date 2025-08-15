import mysql.connector
import os
from dotenv import load_dotenv

# Carga las variables de entorno desde el archivo .env
load_dotenv()

def get_db_connection():
    """
    Establece una conexión a la base de datos MySQL.
    
    Añade un manejo de errores robusto y un timeout para evitar que el proceso se cuelgue.
    """
    try:
        # Intenta conectar con las credenciales del archivo .env
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_DATABASE"),
            # Timeout de conexión de 5 segundos para evitar que se cuelgue
            connect_timeout=5 
        )
        print("DEBUG: Conexión a la base de datos exitosa.")
        return conn
    except mysql.connector.Error as err:
        # Imprime un mensaje de error claro si la conexión falla
        print(f"ERROR: No se pudo conectar a la base de datos. Verifique las credenciales y el servicio de MySQL. Error: {err}")
        return None

def execute_query(query: str, params: tuple = None, fetch_one: bool = False, fetch_all: bool = False):
    """
    Ejecuta una consulta SQL y maneja los resultados y errores.
    
    Retorna los resultados de la consulta o un booleano para operaciones de escritura.
    """
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
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

def create_tables_if_not_exists():
    """
    Crea la tabla password_resets si no existe.
    
    Esta función se llama al iniciar la aplicación.
    """
    query = """
    CREATE TABLE IF NOT EXISTS password_resets (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        token_hash VARCHAR(255) NOT NULL UNIQUE,
        expires_at DATETIME NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """
    if execute_query(query):
        print("Tabla 'password_resets' creada o ya existe.")
    else:
        print("Error al crear la tabla 'password_resets'.")