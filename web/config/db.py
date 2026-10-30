import os
import mysql.connector
from dotenv import load_dotenv

# Carga las variables definidas en el archivo .env
load_dotenv()

def get_connection():
    """Crea y devuelve una conexión activa a la base de datos MySQL."""
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", 3307)),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )