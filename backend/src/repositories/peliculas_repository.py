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
            FROM PELICULAS p
            INNER JOIN FUNCIONES f ON p.id = f.pelicula_id
            INNER JOIN LOCALES_SALAS ls ON f.sala_id = ls.id
            WHERE 1=1
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