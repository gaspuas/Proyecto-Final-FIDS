"""HTTP client del frontend hacia la API REST, con TokenSession Bearer."""
import logging
import os

from flask import has_request_context, session
import requests

LOGGER = logging.getLogger(__name__)
API_REQUEST_TIMEOUT = (3.05, 60)


class BackendAPIError(Exception):
    def __init__(self, message, status_code=502):
        super().__init__(message)
        self.status_code = status_code


def _ruta_protegida(path, method):
    return (
        path == '/api/admin' or path.startswith('/api/admin/')
        or path == '/api/compras' or path.startswith('/api/compras/')
        or path.startswith('/api/novedades/admin/')
        or (path.startswith('/api/novedades') and method.upper() != 'GET')
        or path in ('/api/auth/me', '/api/auth/logout')
    )


def api_request(method, path, *, params=None, payload=None):
    base_url = os.getenv('BACKEND_URL', 'http://127.0.0.1:5001').rstrip('/')
    headers = {}
    if has_request_context() and _ruta_protegida(path, method):
        token = session.get('access_token')
        if token:
            headers['Authorization'] = f'Bearer {token}'
    try:
        response = requests.request(method, f'{base_url}{path}', params=params,
                                    json=payload, headers=headers or None,
                                    timeout=API_REQUEST_TIMEOUT)
    except requests.Timeout as exc:
        LOGGER.warning('Backend API request timed out for %s', path)
        raise BackendAPIError(
            'El backend tardó demasiado en responder. La compra podría haberse '
            'registrado; revisá tu historial antes de volver a intentarlo.', 504,
        ) from exc
    except requests.RequestException as exc:
        LOGGER.warning('Backend API request failed for %s: %s', path, exc)
        raise BackendAPIError('No se pudo establecer conexión con el backend.') from exc

    try:
        result = response.json() if response.content else None
    except ValueError as exc:
        raise BackendAPIError('El backend devolvió una respuesta que no es JSON.',
                              response.status_code) from exc

    if not response.ok:
        message = 'El backend no pudo completar la operación.'
        if isinstance(result, dict):
            errors = result.get('errors') or result.get('errores')
            if isinstance(errors, list) and errors and isinstance(errors[0], str):
                message = '; '.join(errors)
            elif isinstance(errors, list) and errors and isinstance(errors[0], dict):
                message = errors[0].get('description') or errors[0].get('message') or message
            else:
                message = (result.get('message') or result.get('mensaje')
                           or result.get('error') or message)
        raise BackendAPIError(str(message), response.status_code)
    return result
