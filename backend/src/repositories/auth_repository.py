import mysql.connector
from backend.src.utils.db_connection import get_db_connection

def crear_usuario_cliente(nombre, email, password_hash, fecha_nacimiento, recibir_promociones):
    conn = get_db_connection()
    if not conn:
        return False
        
    cursor = None
    try:
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
        if cursor.fetchone():
            return False  

        query = """
            INSERT INTO usuarios (
                nombre, email, password_hash, rol, fecha_registro,
                fecha_nacimiento, acepta_terminos, fecha_aceptacion_terminos,
                recibir_promociones
            ) VALUES (%s, %s, %s, %s, NOW(), %s, 1, NOW(), %s)
        """
        cursor.execute(query, (nombre, email, password_hash, 'cliente', fecha_nacimiento, recibir_promociones))
        conn.commit()
        return True
        
    except mysql.connector.Error as err:
        print(f"Error de base de datos al crear usuario: {err}")
        if conn and conn.is_connected():
            conn.rollback()
        raise err  
        
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

def obtener_usuario_por_email(email):
    conn = get_db_connection()
    if not conn:
        return None
        
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT id, nombre, email, password_hash, rol 
            FROM usuarios
            WHERE email = %s
        """
        cursor.execute(query, (email,))
        usuario = cursor.fetchone()
        return usuario
        
    except mysql.connector.Error as err:
        print(f"Error de Base de Datos en obtener_usuario_por_email: {err}")
        return None
        
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()