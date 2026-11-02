import os
import mysql.connector
from mysql.connector import Error

def get_db_connection():
    """
    Establece y retorna una conexión a la base de datos MySQL 
    usando las variables de entorno o los valores por defecto del proyecto.
    """
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'cine_paradiso_db'),
            port=int(os.getenv('DB_PORT', 3306))
        )
        if connection.is_connected():
            return connection

    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        return None