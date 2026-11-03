"""Client-side server requests for movie data from the backend API."""
import logging
import os

import requests

LOGGER = logging.getLogger(__name__)


class BackendAPIError(Exception):
    """Raised when the frontend cannot consume a valid backend API response."""


def _get_json(path, params=None):
    default_port = os.getenv('PORT', '5000')
    base_url = os.getenv(
        'BACKEND_URL',
        f'http://127.0.0.1:{default_port}',
    ).rstrip('/')
    try:
        response = requests.get(
            f'{base_url}{path}',
            params=params,
            timeout=5,
        )
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError) as exc:
        LOGGER.warning('Backend API request failed for %s: %s', path, exc)
        raise BackendAPIError(
            'No se pudieron obtener los datos de películas del backend.'
        ) from exc


def obtener_peliculas(sede_id=None, fecha=None) -> list[dict]:
    """Fetch the movie listing from the backend API."""
    params = {
        key: value
        for key, value in {'sede_id': sede_id, 'fecha': fecha}.items()
        if value is not None
    }
    payload = _get_json('/api/peliculas', params=params)
    if not isinstance(payload, dict) or not isinstance(payload.get('data'), list):
        raise BackendAPIError('La API del backend devolvió una cartelera inválida.')
    if not all(isinstance(pelicula, dict) for pelicula in payload['data']):
        raise BackendAPIError('La API del backend devolvió películas inválidas.')
    return payload['data']

