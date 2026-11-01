from backend.src.repositories.peliculas_repository import *
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