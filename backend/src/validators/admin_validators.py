from datetime import datetime


def validar_datos_pelicula(data):
    titulo = data.get("titulo")
    sinopsis = data.get("sinopsis")
    duracion = data.get("duracion") or data.get("duracion_minutos")

    if not titulo or not str(titulo).strip():
        return ("BAD_REQUEST", "Campo faltante", "El campo 'titulo' es obligatorio", 400)
    if not sinopsis or not str(sinopsis).strip():
        return ("BAD_REQUEST", "Campo faltante", "El campo 'sinopsis' es obligatorio", 400)
    if duracion is None:
        return ("BAD_REQUEST", "Campo faltante", "El campo 'duracion' es obligatorio", 400)
    if not isinstance(duracion, (int, float)) or isinstance(duracion, bool) or duracion <= 0:
        return ("BAD_REQUEST", "Dato inválido", "El campo 'duracion' debe ser un número mayor a 0", 400)

    return None


def validar_datos_funcion(data):
    pelicula_id = data.get("id_pelicula") or data.get("pelicula_id")
    sala_id = data.get("id_sala") or data.get("sala_id")
    fecha_hora = data.get("fecha_hora")
    precio_base = data.get("precio") or data.get("precio_base")

    if not pelicula_id:
        return ("BAD_REQUEST", "Campo faltante", "El campo 'id_pelicula' es obligatorio", 400)
    if not sala_id:
        return ("BAD_REQUEST", "Campo faltante", "El campo 'id_sala' es obligatorio", 400)
    if not fecha_hora or not str(fecha_hora).strip():
        return ("BAD_REQUEST", "Campo faltante", "El campo 'fecha_hora' es obligatorio", 400)
    if precio_base is None:
        return ("BAD_REQUEST", "Campo faltante", "El campo 'precio' es obligatorio", 400)
    if not isinstance(precio_base, (int, float)) or isinstance(precio_base, bool) or precio_base < 0:
        return ("BAD_REQUEST", "Dato inválido", "El campo 'precio' debe ser un número mayor o igual a 0", 400)

    return None


def validar_datos_qr(data):
    codigo_qr = data.get("codigo_qr")

    if not codigo_qr or not str(codigo_qr).strip():
        return ("BAD_REQUEST", "Campo faltante", "El campo 'codigo_qr' es obligatorio", 400)

    return None


def validar_rango_fechas(desde, hasta):
    if not desde or not hasta:
        return ("BAD_REQUEST", "Parámetros faltantes", "Los parámetros 'desde' y 'hasta' son obligatorios (ej. YYYY-MM-DD)", 400)

    try:
        fecha_desde = datetime.strptime(desde, "%Y-%m-%d")
        fecha_hasta = datetime.strptime(hasta, "%Y-%m-%d")
        if fecha_desde > fecha_hasta:
            return ("BAD_REQUEST", "Rango inválido", "La fecha 'desde' no puede ser posterior a 'hasta'", 400)
    except ValueError:
        return ("BAD_REQUEST", "Formato inválido", "Las fechas deben tener el formato YYYY-MM-DD", 400)

    return None