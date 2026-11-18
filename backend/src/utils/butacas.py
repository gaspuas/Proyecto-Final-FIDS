"""Códigos de butaca estilo cine: letra de fila + número de columna (A1, C7)."""
import re

_PATRON_CODIGO = re.compile(r'^([A-Z])([1-9][0-9]?)$')


def letra_fila(indice: int) -> str:
    """Devuelve la letra de la fila (0 -> 'A', 1 -> 'B', ...)."""
    return chr(ord('A') + indice)


def generar_codigos(filas: int, columnas: int) -> list[str]:
    """Genera todos los códigos de una sala, fila por fila."""
    return [
        f'{letra_fila(fila)}{columna}'
        for fila in range(filas)
        for columna in range(1, columnas + 1)
    ]


def es_codigo_valido(codigo, filas: int, columnas: int) -> bool:
    """Indica si el código existe en una sala de `filas` x `columnas`."""
    if not isinstance(codigo, str):
        return False
    coincidencia = _PATRON_CODIGO.match(codigo)
    if not coincidencia:
        return False
    fila = ord(coincidencia.group(1)) - ord('A')
    columna = int(coincidencia.group(2))
    return fila < filas and 1 <= columna <= columnas
