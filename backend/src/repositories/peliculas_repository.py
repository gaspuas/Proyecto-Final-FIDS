import mysql.connector
from backend.src.utils.db_connection import get_db_connection

def listar_peliculas_cartelera(sede_id=None, fecha=None):
    conn = get_db_connection()
    if not conn:
        raise Exception("Fallo en la conexión a la base de datos.")
        
    cursor = None
    try:
        # Usamos dictionary=True para retornar los datos como JSON directamente
        cursor = conn.cursor(dictionary=True)
        
        # Filtramos uniendo con FUNCIONES para traer solo películas activas.
        # LOCALES_SALAS contiene el mapeo físico de la sala/sede.
        query = """
            SELECT DISTINCT p.id, p.api_id, p.titulo, p.sinopsis, 
                            p.poster_url, p.duracion_minutos, 
                            p.clasificacion, p.genero, p.director, p.es_reestreno
            FROM peliculas p
            INNER JOIN funciones f ON p.id = f.pelicula_id
            INNER JOIN locales_salas ls ON f.sala_id = ls.id
            WHERE f.fecha_hora >= NOW()
        """
        
        parametros = []
        
        if sede_id:
            query += " AND ls.id = %s"
            parametros.append(sede_id)
            
        if fecha:
            # Se usa la función DATE() de SQL para comparar la fecha extraída de un DATETIME
            query += " AND DATE(f.fecha_hora) = %s"
            parametros.append(fecha)
            
        cursor.execute(query, tuple(parametros))
        peliculas = cursor.fetchall()
        return peliculas
        
    except mysql.connector.Error as err:
        print(f"Error de base de datos en listar_peliculas_cartelera: {err}")
        raise err  
        
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

def obtener_pelicula_por_id(pelicula_id):
    conn = get_db_connection()
    if not conn:
        raise Exception("Fallo en la conexión a la base de datos.")
        
    cursor = None
    try:
        # Se retorna un diccionario para mapearlo directamente a JSON
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT id, api_id, titulo, sinopsis, poster_url, 
                   duracion_minutos, clasificacion, genero, 
                   director, es_reestreno
            FROM peliculas
            WHERE id = %s
        """
        # Ejecución segura previniendo inyección SQL
        cursor.execute(query, (pelicula_id,))
        pelicula = cursor.fetchone()
        return pelicula
        
    except mysql.connector.Error as err:
        print(f"Error de base de datos en obtener_pelicula_por_id: {err}")
        raise err  
        
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


def listar_todas_las_peliculas():
    conn = get_db_connection()
    if not conn:
        raise Exception("Fallo en la conexión a la base de datos.")

    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, api_id, titulo, sinopsis, poster_url,
                   duracion_minutos, clasificacion, genero, director, es_reestreno
            FROM peliculas
            ORDER BY titulo ASC
        """)
        return cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Error de base de datos en listar_todas_las_peliculas: {err}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


def listar_resenas_pelicula(pelicula_id):
    conn = get_db_connection()
    if not conn:
        raise Exception("Fallo en la conexión a la base de datos.")

    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT u.nombre AS nombre_usuario, r.puntuacion, r.comentario, r.fecha
            FROM resenas AS r
            INNER JOIN usuarios AS u ON u.id = r.usuario_id
            WHERE r.pelicula_id = %s
            ORDER BY r.fecha DESC, r.id DESC
        """, (pelicula_id,))
        return cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Error de base de datos en listar_resenas_pelicula: {err}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()