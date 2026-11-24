from backend.src.repositories.peliculas_repository import (
    listar_peliculas_cartelera,
    listar_resenas_pelicula,
    listar_todas_las_peliculas,
    obtener_pelicula_por_id,
    actualizar_poster_pelicula_db,
)
from backend.src.validators.peliculas_validators import *

def procesar_obtener_cartelera(sede_id, fecha):
    # 1. Validar parámetros opcionales
    es_valido, mensaje_error = validar_query_params_cartelera(sede_id, fecha)
    if not es_valido:
        return {'exito': False, 'mensaje': mensaje_error, 'tipo_error': 'VALIDATION'}

    # 2. Consultar cartelera a la base de datos
    try:
        peliculas = listar_peliculas_cartelera(sede_id, fecha)
        return {'exito': True, 'datos': peliculas}
        
    except Exception as e:
        return {'exito': False, 'mensaje': str(e), 'tipo_error': 'INTERNAL_ERROR'}

def procesar_obtener_pelicula(pelicula_id):
    es_valido, mensaje_error = validar_id_pelicula(pelicula_id)
    if not es_valido:
        return {'exito': False, 'mensaje': mensaje_error, 'tipo_error': 'VALIDATION'}

    try:
        pelicula = obtener_pelicula_por_id(pelicula_id)
        if not pelicula:
            return {'exito': False, 'mensaje': 'Película no encontrada en el sistema.', 'tipo_error': 'NOT_FOUND'}
            
        return {
            'exito': True, 
            'mensaje': 'Detalle de la película obtenido exitosamente.', 
            'datos': pelicula
        }
        
    except Exception as e:
        return {'exito': False, 'mensaje': str(e), 'tipo_error': 'INTERNAL_ERROR'}


def procesar_listar_todas_las_peliculas():
    try:
        return {'exito': True, 'datos': listar_todas_las_peliculas()}
    except Exception as e:
        return {'exito': False, 'mensaje': str(e), 'tipo_error': 'INTERNAL_ERROR'}


def procesar_listar_resenas(pelicula_id):
    es_valido, mensaje_error = validar_id_pelicula(pelicula_id)
    if not es_valido:
        return {'exito': False, 'mensaje': mensaje_error, 'tipo_error': 'VALIDATION'}
    try:
        return {'exito': True, 'datos': listar_resenas_pelicula(pelicula_id)}
    except Exception as e:
        return {'exito': False, 'mensaje': str(e), 'tipo_error': 'INTERNAL_ERROR'}


def procesar_actualizar_poster_pelicula(pelicula_id, poster_url):
    """Conserva el resto de la ficha y actualiza la imagen de Cartelera."""
    es_valido, mensaje_error = validar_id_pelicula(pelicula_id)
    if not es_valido:
        return None, ("VALIDATION", "ID inválido", mensaje_error, 400)
    if not isinstance(poster_url, str) or not poster_url.strip() or len(poster_url) > 500:
        return None, ("VALIDATION", "Imagen inválida", "Falta una imagen válida (máximo 500 caracteres).", 400)
    from urllib.parse import urlsplit
    destino = urlsplit(poster_url)
    if not ((poster_url.startswith('/static/img/') and '..' not in poster_url and not poster_url.startswith('//'))
            or (destino.scheme in ('https', 'http') and destino.netloc)):
        return None, ("VALIDATION", "Imagen inválida", "Usá una URL HTTP(S) o una imagen del proyecto.", 400)
    try:
        if not obtener_pelicula_por_id(pelicula_id):
            return None, ("NOT_FOUND", "Película no encontrada", "La película no existe.", 404)
        actualizar_poster_pelicula_db(pelicula_id, poster_url)
        return {"id": pelicula_id, "poster_url": poster_url}, None
    except Exception:
        return None, ("INTERNAL_SERVER_ERROR", "Error de base de datos", "No se pudo actualizar el póster.", 500)
