from backend.src.repositories.peliculas_repository import (
    listar_peliculas_cartelera,
    listar_resenas_pelicula,
    listar_todas_las_peliculas,
    obtener_pelicula_por_id,
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