"""Consulta de novedades al backend desde Flask (nunca desde JS del navegador)."""
import logging
import os
from urllib.parse import urlparse
import requests

LOGGER = logging.getLogger(__name__)


def _enlace_valido(valor):
    """Permite rutas internas o enlaces http(s), nunca javascript: ni //dominio."""
    if not isinstance(valor, str):
        return None
    valor = valor.strip()
    if valor.startswith('/') and not valor.startswith('//'):
        return valor
    parsed = urlparse(valor)
    if parsed.scheme in ('http', 'https') and parsed.netloc:
        return valor
    return None


def obtener_novedades():
    """Devuelve novedades publicables; [] si el endpoint todavía no existe.

    PENDIENTE BACKEND: implementar GET /api/novedades, devolviendo JSON
    en forma de lista, o {"novedades": [...]}. El endpoint debe filtrar
    activo/fechas y ordenar por `orden`. Ver docs/CARRUSEL_BACKEND.md.
    """
    base_url = os.getenv('BACKEND_URL', 'http://127.0.0.1:5001').rstrip('/')
    try:
        response = requests.get(f'{base_url}/api/novedades', timeout=3)
        response.raise_for_status()
        datos = response.json()
        if isinstance(datos, dict):
            datos = datos.get('novedades', [])
        if not isinstance(datos, list):
            LOGGER.warning('Novedades: respuesta inesperada del backend')
            return []
        novedades = []
        for dato in datos:
            if not isinstance(dato, dict) or not dato.get('titulo') or not dato.get('imagen_url'):
                continue
            novedades.append({
                'id': dato.get('id'),
                'titulo': str(dato['titulo']),
                'descripcion': str(dato.get('descripcion') or ''),
                'imagen_url': str(dato['imagen_url']),
                'tipo': str(dato.get('tipo') or 'novedad'),
                'enlace': _enlace_valido(dato.get('enlace')),
                'orden': dato.get('orden', 0),
            })
        return novedades
    except (requests.RequestException, ValueError, TypeError) as exc:
        LOGGER.info('Novedades no disponibles (backend pendiente): %s', exc)
        return []
