"""Client-side server requests for movie data from the backend API."""
from frontend.web.services.api_client import BackendAPIError, api_request


def obtener_peliculas(sede_id=None, fecha=None) -> list[dict]:
    """Fetch the movie listing from the backend API."""
    params = {
        key: value
        for key, value in {'sede_id': sede_id, 'fecha': fecha}.items()
        if value is not None
    }
    payload = api_request('GET', '/api/peliculas', params=params)
    if not isinstance(payload, dict) or not isinstance(payload.get('data'), list):
        raise BackendAPIError('La API del backend devolvió una cartelera inválida.')
    if not all(isinstance(pelicula, dict) for pelicula in payload['data']):
        raise BackendAPIError('La API del backend devolvió películas inválidas.')
    return payload['data']


def obtener_todas_las_peliculas() -> list[dict]:
    payload = api_request('GET', '/api/admin/peliculas')
    if not isinstance(payload, dict) or not isinstance(payload.get('data'), list):
        raise BackendAPIError('La API del backend devolvió una lista inválida.')
    return payload['data']


def obtener_pelicula(pelicula_id):
    payload = api_request('GET', f'/api/peliculas/{pelicula_id}')
    if not isinstance(payload, dict) or not isinstance(payload.get('data'), dict):
        raise BackendAPIError('La API del backend devolvió un detalle inválido.')
    return payload['data']


def obtener_resenas(pelicula_id):
    payload = api_request('GET', f'/api/peliculas/{pelicula_id}/resenas')
    if not isinstance(payload, dict) or not isinstance(payload.get('resenas'), list):
        raise BackendAPIError('La API del backend devolvió una lista de reseñas inválida.')
    return payload['resenas']


def crear_pelicula(datos):
    return api_request('POST', '/api/admin/peliculas', payload=datos)


def crear_funcion(datos):
    return api_request('POST', '/api/admin/funciones', payload=datos)
