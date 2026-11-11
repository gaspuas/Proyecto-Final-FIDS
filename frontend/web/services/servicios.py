from frontend.web.services.api_client import BackendAPIError, api_request


def obtener_servicios():
    payload = api_request('GET', '/api/servicios')
    if not isinstance(payload, dict) or not isinstance(payload.get('data'), list):
        raise BackendAPIError('La API del backend devolvió una lista de servicios inválida.')
    return payload['data']
