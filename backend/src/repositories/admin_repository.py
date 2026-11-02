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
            INSERT INTO PELICULAS (api_id, titulo, sinopsis, poster_url, duracion_minutos, clasificacion, genero, director, es_reestreno)
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

def insertar_funcion_db(pelicula_id, sala_id, fecha_hora, precio_base, idioma="Español", formato="2D"):
    conn = get_db_connection()
    if not conn:
        return None
    
    cursor = None
    try:
        cursor = conn.cursor()
        query = """
            INSERT INTO FUNCIONES (pelicula_id, sala_id, fecha_hora, precio_base, idioma, formato)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        valores = (pelicula_id, sala_id, fecha_hora, precio_base, idioma, formato)
        
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
        
        query = "SELECT id, estado_qr FROM COMPRAS WHERE codigo_qr = %s"
        cursor.execute(query, (codigo_qr,))
        compra = cursor.fetchone()
        
        if not compra:
            return {"valido": False, "razon": "NOT_FOUND", "mensaje": "El código QR no pertenece a ninguna compra registrada"}
        
        if compra['estado_qr'] == 'usado':
            return {"valido": False, "razon": "ALREADY_USED", "mensaje": "El ticket QR ya fue utilizado anteriormente"}
            
        if compra['estado_qr'] == 'cancelado':
            return {"valido": False, "razon": "CANCELLED", "mensaje": "La compra asociada a este QR fue cancelada"}
            
        query_actualizar = "UPDATE COMPRAS SET estado_qr = 'usado' WHERE id = %s"
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
            FROM COMPRAS
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