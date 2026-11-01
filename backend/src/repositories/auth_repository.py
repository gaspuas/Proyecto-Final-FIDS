from backend.src.utils.db_connection import get_db_connection

def crear_usuario_cliente(nombre, email, password_hash):
    conexion = get_db_connection()
    cursor = conexion.cursor()
    try:
        # Verificar si el email ya existe
        cursor.execute("SELECT id FROM USUARIOS WHERE email = %s", (email,))
        if cursor.fetchone():
            return False  # El usuario ya existe

        # Inserción con SQL puro (Regla 6)
        query = """
            INSERT INTO USUARIOS (nombre, email, password_hash, rol, fecha_registro)
            VALUES (%s, %s, %s, %s, NOW())
        """
        # Se fuerza el rol a 'cliente' por defecto para este endpoint
        cursor.execute(query, (nombre, email, password_hash, 'cliente'))
        conexion.commit()
        return True
    except Exception as e:
        conexion.rollback()
        raise e
    finally:
        cursor.close()
        conexion.close()