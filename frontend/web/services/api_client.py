"""HTTP client used by frontend routes to consume the backend API."""
import logging
import os

import requests

LOGGER = logging.getLogger(__name__)


class BackendAPIError(Exception):
    def __init__(self, message, status_code=502):
        super().__init__(message)
        self.status_code = status_code


def api_request(method, path, *, params=None, payload=None):
    default_port = os.getenv('PORT', '5000')
    base_url = os.getenv(
        'BACKEND_URL',
        f'http://127.0.0.1:{default_port}',
    ).rstrip('/')
    try:
        response = requests.request(
            method,
            f'{base_url}{path}',
            params=params,
            json=payload,
            timeout=5,
        )
    except requests.RequestException as exc:
        LOGGER.warning('Backend API request failed for %s: %s', path, exc)
        raise BackendAPIError(
            'No se pudo establecer conexión con el backend.'
        ) from exc

    try:
        result = response.json() if response.content else None
    except ValueError as exc:
        raise BackendAPIError(
            'El backend devolvió una respuesta que no es JSON.',
            response.status_code,
        ) from exc

    if not response.ok:
        message = 'El backend no pudo completar la operación.'
        if isinstance(result, dict):
            errors = result.get('errors')
            if isinstance(errors, list) and errors and isinstance(errors[0], dict):
                message = errors[0].get('description') or errors[0].get('message') or message
            else:
                message = result.get('message') or result.get('mensaje') or message
        raise BackendAPIError(str(message), response.status_code)

    return result
