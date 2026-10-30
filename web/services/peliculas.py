"""Datos de peliculas (version standalone, sin backend).

En la rama `integracion-api` estos mismos services consumen la API
store-api via HTTP; aca devuelven los datos de ejemplo de
web/constants.py con la misma forma que los DTOs de la API.
"""
from web.constants import PELICULAS_EJEMPLO



def obtener_peliculas(categoria_id: int = None, texto: str = None) -> list[dict]:
    """Devuelve los peliculas de ejemplo, con los mismos filtros que la API."""
    resultado = PELICULAS_EJEMPLO

    if categoria_id:
        resultado = [pelicula for pelicula in resultado if pelicula['categoria']['id'] == categoria_id]

    if texto:
        resultado = [pelicula for pelicula in resultado if texto.lower() in pelicula['titulo'].lower()]

    return resultado
