from frontend.web.services.api_client import BackendAPIError, api_request


def obtener_salas():
    payload = api_request('GET', '/api/admin/salas')
    if not isinstance(payload, dict) or not isinstance(payload.get('data'), list):
        raise BackendAPIError('La API del backend devolvió una lista de salas inválida.')
    return payload['data']
