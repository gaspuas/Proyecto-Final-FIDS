"""Compras del usuario consultadas a la API."""
from frontend.web.services.api_client import BackendAPIError, api_request


def crear_compra(id_usuario, id_funcion, butacas, servicios):
    return api_request(
        'POST',
        '/api/compras',
        payload={
            'id_usuario': id_usuario,
            'id_funcion': id_funcion,
            'butacas': butacas,
            'servicios': servicios,
        },
    )


def cancelar_compra(id_compra):
    return api_request('PATCH', f'/api/compras/{id_compra}/cancelar')


def obtener_compras_usuario(id_usuario):
    payload = api_request('GET', f'/api/compras/usuario/{id_usuario}')
    if not isinstance(payload, dict) or not isinstance(payload.get('compras'), list):
        raise BackendAPIError('La API del backend devolvió un historial de compras inválido.')
    return payload['compras']


def obtener_compra(id_usuario, id_compra):
    """Devuelve la compra solo si pertenece al usuario; si no, None."""
    return next(
        (compra for compra in obtener_compras_usuario(id_usuario) if compra.get('id') == id_compra),
        None,
    )
