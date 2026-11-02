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

