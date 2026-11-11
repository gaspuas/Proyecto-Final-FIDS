"""Funciones, servicios y compras consultados a la API."""
from frontend.web.services.api import consultar_api


def obtener_funcion(funcion_id):
    """Busca una funcion vigente. La API solo lista funciones futuras."""
    datos = consultar_api(
        'GET', '/api/funciones',
        mensaje_error='No pudimos consultar la función elegida.',
    )
    funciones = datos.get('funciones') if isinstance(datos, dict) else None
    return next(
        (funcion for funcion in funciones or [] if funcion.get('id') == funcion_id),
        None,
    )


def listar_servicios():
    datos = consultar_api(
        'GET', '/api/servicios',
        mensaje_error='No pudimos cargar los servicios adicionales.',
    )
    servicios = datos.get('data') if isinstance(datos, dict) else None
    return servicios if isinstance(servicios, list) else []


def crear_compra(id_usuario, id_funcion, butacas, servicios):
    return consultar_api(
        'POST', '/api/compras',
        json={
            'id_usuario': id_usuario,
            'id_funcion': id_funcion,
            'butacas': butacas,
            'servicios': servicios,
        },
        esperados=(201,),
        mensaje_error='No pudimos registrar la compra.',
    )


def obtener_compra(id_usuario, id_compra):
    """Devuelve la compra solo si pertenece al usuario; si no, None."""
    datos = consultar_api(
        'GET', f'/api/compras/usuario/{id_usuario}',
        mensaje_error='No pudimos consultar tus compras.',
    )
    compras = datos.get('compras') if isinstance(datos, dict) else None
    return next(
        (compra for compra in compras or [] if compra.get('id') == id_compra),
        None,
    )


def cancelar_compra(id_compra):
    return consultar_api(
        'PATCH', f'/api/compras/{id_compra}/cancelar',
        mensaje_error='No pudimos cancelar la compra.',
    )
