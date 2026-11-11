from frontend.web.services.api_client import BackendAPIError, api_request


def obtener_funciones(pelicula_id):
    payload = api_request(
        'GET',
        '/api/funciones',
        params={'pelicula_id': pelicula_id},
    )
    if not isinstance(payload, dict) or not isinstance(payload.get('funciones'), list):
        raise BackendAPIError('La API del backend devolvió una lista de funciones inválida.')
    return payload['funciones']


def obtener_funcion(funcion_id):
    payload = api_request('GET', f'/api/funciones/{funcion_id}')
    if not isinstance(payload, dict) or not isinstance(payload.get('funcion'), dict):
        raise BackendAPIError('La API del backend devolvió una función inválida.')
    return payload['funcion']


def obtener_butacas(funcion_id):
    payload = api_request('GET', f'/api/funciones/{funcion_id}/butacas')
    if not isinstance(payload, dict) or not isinstance(payload.get('butacas'), list):
        raise BackendAPIError('La API del backend devolvió un mapa de butacas inválido.')
    return payload
