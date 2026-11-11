from datetime import datetime
from decimal import Decimal

from backend.src.repositories.funciones_repository import (
    obtener_butacas_ocupadas_db,
    obtener_funciones_db,
    obtener_funcion_por_id_db,
)


def _serializar_fecha(valor):
    if valor is None:
        return None
    if isinstance(valor, datetime):
        return valor.isoformat(sep=' ')
    return str(valor)


def _serializar_funcion(funcion):
    if not funcion:
        return None
    funcion_serializada = dict(funcion)
    if 'fecha_hora' in funcion_serializada:
        funcion_serializada['fecha_hora'] = _serializar_fecha(funcion_serializada['fecha_hora'])
    if isinstance(funcion_serializada.get('precio_base'), Decimal):
        funcion_serializada['precio_base'] = float(funcion_serializada['precio_base'])
    return funcion_serializada


def listar_funciones_service(
    pelicula_id: int | None = None,
    sala_id: int | None = None,
    formato: str | None = None,
    idioma: str | None = None,
):
    """Devuelve las funciones vigentes con filtros opcionales."""
    if pelicula_id is not None:
        if not isinstance(pelicula_id, int) or isinstance(pelicula_id, bool) or pelicula_id <= 0:
            return None, "El campo 'pelicula_id' debe ser un entero positivo.", 400

    if sala_id is not None:
        if not isinstance(sala_id, int) or isinstance(sala_id, bool) or sala_id <= 0:
            return None, "El campo 'sala_id' debe ser un entero positivo.", 400

    if formato is not None:
        if not isinstance(formato, str):
            return None, "El campo 'formato' debe ser un texto válido.", 400
        formato = formato.strip()
        if not formato:
            return None, "El campo 'formato' no puede estar vacío.", 400

    if idioma is not None:
        if not isinstance(idioma, str):
            return None, "El campo 'idioma' debe ser un texto válido.", 400
        idioma = idioma.strip()
        if not idioma:
            return None, "El campo 'idioma' no puede estar vacío.", 400

    funciones = obtener_funciones_db(
        pelicula_id=pelicula_id,
        sala_id=sala_id,
        formato=formato,
        idioma=idioma,
    )
    funciones_response = [
        _serializar_funcion(funcion) for funcion in funciones
    ]
    return funciones_response, None, 200


def consultar_butacas_funcion_service(id_funcion: int):
    """Retorna el estado de cada butaca para una función específica."""
    if not isinstance(id_funcion, int) or isinstance(id_funcion, bool) or id_funcion <= 0:
        return None, "El ID de la función debe ser un entero positivo.", 400

    funcion = obtener_funcion_por_id_db(id_funcion)
    if not funcion:
        return None, f"Función con ID {id_funcion} no encontrada.", 404

    capacidad_total = int(funcion['capacidad_total'])
    ocupadas = obtener_butacas_ocupadas_db(id_funcion)

    butacas = []
    ocupadas_lista = []
    libres_lista = []

    for numero in range(1, capacidad_total + 1):
        valor = str(numero)
        estado = 'ocupada' if valor in ocupadas else 'libre'
        if estado == 'ocupada':
            ocupadas_lista.append(numero)
        else:
            libres_lista.append(numero)

        butacas.append({
            'numero': numero,
            'estado': estado,
            'libre': estado == 'libre',
        })

    return {
        'funcion_id': id_funcion,
        'capacidad_total': capacidad_total,
        'filas': int(funcion['filas']),
        'columnas': int(funcion['columnas']),
        'ocupadas': ocupadas_lista,
        'libres': libres_lista,
        'butacas': butacas,
    }, None, 200


def consultar_funcion_service(id_funcion: int):
    """Returns one function with its room details, if it exists."""
    if not isinstance(id_funcion, int) or isinstance(id_funcion, bool) or id_funcion <= 0:
        return None, "El ID de la función debe ser un entero positivo.", 400
    funcion = obtener_funcion_por_id_db(id_funcion)
    if not funcion:
        return None, f"Función con ID {id_funcion} no encontrada.", 404
    return _serializar_funcion(funcion), None, 200
