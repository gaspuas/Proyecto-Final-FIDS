"""Cliente HTTP de la API REST para la capa web.

Todas las peticiones salen desde Python con requests; el navegador nunca
llama a la API.
"""
import logging
import os

import requests

LOGGER = logging.getLogger(__name__)

TIMEOUT_SEGUNDOS = 5
MENSAJE_SIN_CONEXION = 'No pudimos conectarnos con el servidor. Intentá de nuevo en unos minutos.'


class ErrorApi(Exception):
    """La API no respondió o devolvió un error; `mensaje` se puede mostrar al usuario."""

    def __init__(self, mensaje, status=None):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.status = status


def _base_url():
    default_port = os.getenv('PORT', '5000')
    return os.getenv('BACKEND_URL', f'http://127.0.0.1:{default_port}').rstrip('/')


def _descripcion_error(datos):
    """Extrae el texto de error del formato {"errors": [{...}]} que usa la API."""
    try:
        error = datos['errors'][0]
        return error.get('description') or error.get('message')
    except (KeyError, IndexError, TypeError, AttributeError):
        return None


def consultar_api(metodo, ruta, *, json=None, esperados=(200,), mensaje_error):
    """Llama a la API y devuelve el JSON de la respuesta.

    Lanza ErrorApi si no hay conexion, si el status no es uno de `esperados`
    o si la respuesta no es JSON.
    """
    try:
        respuesta = requests.request(
            metodo, f'{_base_url()}{ruta}', json=json, timeout=TIMEOUT_SEGUNDOS
        )
    except requests.RequestException as exc:
        LOGGER.warning('API no disponible en %s %s: %s', metodo, ruta, exc)
        raise ErrorApi(MENSAJE_SIN_CONEXION) from exc

    try:
        datos = respuesta.json()
    except ValueError:
        datos = None

    if respuesta.status_code not in esperados:
        LOGGER.info('API %s %s respondio %s', metodo, ruta, respuesta.status_code)
        raise ErrorApi(
            _descripcion_error(datos) or mensaje_error, respuesta.status_code
        )
    if datos is None:
        raise ErrorApi(mensaje_error, respuesta.status_code)
    return datos
