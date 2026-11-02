import mysql.connector
from backend.src.utils.db_connection import get_db_connection


def listar_servicios():
    """Devuelve todos los servicios adicionales disponibles (catálogo completo)."""
    conn = get_db_connection()
    if not conn:
        raise Exception("Fallo en la conexión a la base de datos.")

    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT id, nombre, categoria, precio, descripcion
            FROM servicios
            ORDER BY categoria ASC, nombre ASC
        """
        cursor.execute(query)
        return cursor.fetchall()

    except mysql.connector.Error as err:
        print(f"Error de base de datos en listar_servicios: {err}")
        raise err

    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
