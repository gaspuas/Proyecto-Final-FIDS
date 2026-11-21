"""Intermediario Flask hacia la API REST de novedades."""
from frontend.web.services.api_client import BackendAPIError, api_request


def listar_novedades_admin():
    data = api_request('GET', '/api/novedades/admin/todas')
    if not isinstance(data, list):
        raise BackendAPIError('El backend devolvió novedades inválidas.')
    return data


def crear_novedad(data):
    return api_request('POST', '/api/novedades', payload=data)


def editar_novedad(novedad_id, data):
    return api_request('PUT', f'/api/novedades/{novedad_id}', payload=data)


def eliminar_novedad(novedad_id):
    return api_request('DELETE', f'/api/novedades/{novedad_id}')
