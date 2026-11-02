from backend.src.repositories.servicios_repository import *


def procesar_listar_servicios():
    try:
        servicios = listar_servicios()

        # precio es DECIMAL en MySQL (llega como Decimal): lo pasamos a float para el JSON
        for servicio in servicios:
            servicio['precio'] = float(servicio['precio'])

        return {
            'exito': True,
            'mensaje': 'Servicios obtenidos exitosamente.',
            'datos': servicios
        }

    except Exception as e:
        return {'exito': False, 'mensaje': str(e), 'tipo_error': 'INTERNAL_ERROR'}
