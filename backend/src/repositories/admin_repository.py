import mysql.connector
from backend.src.utils.db_connection import get_db_connection

def insertar_pelicula_db(titulo, sinopsis, duracion_minutos, poster_url, api_id=None, clasificacion=None, genero=None, director=None, es_reestreno=False):
    conn = get_db_connection()
    if not conn:
        return None
    
    cursor = None
    try:
        cursor = conn.cursor()
        query = """
            INSERT INTO peliculas (api_id, titulo, sinopsis, poster_url, duracion_minutos, clasificacion, genero, director, es_reestreno)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        valores = (api_id, titulo, sinopsis, poster_url, duracion_minutos, clasificacion, genero, director, es_reestreno)
        
        cursor.execute(query, valores)
        conn.commit()
        
        return cursor.lastrowid

    except mysql.connector.Error as err:
        print(f"Error al insertar película: {err}")
        if conn:
            conn.rollback()
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

class FuncionSuperpuestaError(Exception):
    """La sala ya tiene una función en ese horario."""


def insertar_funcion_db(pelicula_id, sala_id, fecha_hora, precio_base, idioma="Español", formato="2D", imagen_url=None):
    conn = get_db_connection()
    if not conn:
        return None

    cursor = None
    try:
        cursor = conn.cursor()
        # Bloquea la sala hasta el commit: dos altas simultáneas se controlan de a una.
        cursor.execute("SELECT id FROM locales_salas WHERE id = %s FOR UPDATE", (sala_id,))
        cursor.fetchone()

        # Dos funciones se superponen si cada una empieza antes de que termine la otra.
        cursor.execute(
            """
            SELECT f.id
            FROM funciones AS f
            INNER JOIN peliculas AS p ON p.id = f.pelicula_id
            WHERE f.sala_id = %s
              AND f.fecha_hora < DATE_ADD(%s, INTERVAL (
                    SELECT duracion_minutos FROM peliculas WHERE id = %s
                  ) MINUTE)
              AND DATE_ADD(f.fecha_hora, INTERVAL p.duracion_minutos MINUTE) > %s
            LIMIT 1
            """,
            (sala_id, fecha_hora, pelicula_id, fecha_hora),
        )
        if cursor.fetchone():
            conn.rollback()
            raise FuncionSuperpuestaError()

        query = """
            INSERT INTO funciones (pelicula_id, sala_id, fecha_hora, precio_base, idioma, formato, imagen_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        valores = (pelicula_id, sala_id, fecha_hora, precio_base, idioma, formato, imagen_url)
        
        cursor.execute(query, valores)
        conn.commit()
        
        return cursor.lastrowid
    
    except mysql.connector.Error as err:
        print(f"Error al insertar función en BD: {err}")
        if conn:
            conn.rollback()
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def validar_y_marcar_qr_db(codigo_qr):
    conn = get_db_connection()
    if not conn:
        return None
    
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        
        query = "SELECT id, estado_qr FROM compras WHERE codigo_qr = %s"
        cursor.execute(query, (codigo_qr,))
        compra = cursor.fetchone()
        
        if not compra:
            return {"valido": False, "razon": "NOT_FOUND", "mensaje": "El código QR no pertenece a ninguna compra registrada"}
        
        if compra['estado_qr'] == 'usado':
            return {"valido": False, "razon": "ALREADY_USED", "mensaje": "El ticket QR ya fue utilizado anteriormente"}
            
        if compra['estado_qr'] == 'cancelado':
            return {"valido": False, "razon": "CANCELLED", "mensaje": "La compra asociada a este QR fue cancelada"}
            
        query_actualizar = "UPDATE compras SET estado_qr = 'usado' WHERE id = %s"
        cursor.execute(query_actualizar, (compra['id'],))
        conn.commit()
        
        return {"valido": True, "mensaje": "Acceso permitido. Ticket marcado como usado con éxito"}
        
    except mysql.connector.Error as err:
        print(f"Error al validar QR en la BD: {err}")
        if conn:
            conn.rollback()
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def obtener_metricas_dashboard_db(desde, hasta):
    conn = get_db_connection()
    if not conn:
        return None
    
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        
        
        query = """
            SELECT id, monto_total
            FROM compras
            WHERE DATE(fecha_compra) >= %s 
              AND DATE(fecha_compra) <= %s 
              AND estado_qr != 'cancelado'
        """
        cursor.execute(query, (desde, hasta))
        compras = cursor.fetchall()
        
        
        total_compras = len(compras)
        facturacion_total = sum(c['monto_total'] for c in compras) if compras else 0.0

        return {
            "total_compras": total_compras,
            "facturacion_total": facturacion_total
        }

    except mysql.connector.Error as err:
        print(f"Error al obtener métricas en BD: {err}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def listar_salas_db():
    conn = get_db_connection()
    if not conn:
        raise Exception("Fallo en la conexión a la base de datos.")

    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, nombre_local, numero_sala, capacidad_total, filas, columnas
            FROM locales_salas
            ORDER BY nombre_local, numero_sala
        """)
        return cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Error al consultar salas: {err}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()