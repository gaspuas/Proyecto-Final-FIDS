from backend.src.repositories.admin_repository import (
    listar_salas_db,
    insertar_pelicula_db,
    insertar_funcion_db,
    validar_y_marcar_qr_db,
    obtener_metricas_dashboard_db,
)
from backend.src.validators.admin_validators import (
    validar_datos_pelicula,
    validar_datos_funcion,
    validar_datos_qr,
    validar_rango_fechas,
)


def crear_pelicula_service(data):
    error = validar_datos_pelicula(data)
    if error:
        return None, error

    titulo = data.get("titulo")
    sinopsis = data.get("sinopsis")
    duracion = data.get("duracion") or data.get("duracion_minutos")
    poster_url = data.get("poster_url")
    api_id = data.get("api_id")
    clasificacion = data.get("clasificacion")
    genero = data.get("genero")
    director = data.get("director")
    es_reestreno = data.get("es_reestreno", False)

    id_creado = insertar_pelicula_db(
        titulo=titulo,
        sinopsis=sinopsis,
        duracion_minutos=duracion,
        poster_url=poster_url,
        api_id=api_id,
        clasificacion=clasificacion,
        genero=genero,
        director=director,
        es_reestreno=es_reestreno,
    )

    if not id_creado:
        return None, ("INTERNAL_ERROR", "Error de base de datos", "No se pudo registrar la película", 500)

    respuesta = {
        "id": id_creado,
        "titulo": titulo,
        "mensaje": "Película registrada con éxito",
    }
    return respuesta, None


def crear_funcion_service(data):
    error = validar_datos_funcion(data)
    if error:
        return None, error

    pelicula_id = data.get("id_pelicula") or data.get("pelicula_id")
    sala_id = data.get("id_sala") or data.get("sala_id")
    fecha_hora = data.get("fecha_hora")
    precio_base = data.get("precio") or data.get("precio_base")
    idioma = data.get("idioma", "Español")
    formato = data.get("formato", "2D")

    id_creado = insertar_funcion_db(
        pelicula_id=pelicula_id,
        sala_id=sala_id,
        fecha_hora=fecha_hora,
        precio_base=precio_base,
        idioma=idioma,
        formato=formato,
    )

    if not id_creado:
        return None, ("INTERNAL_ERROR", "Error de base de datos", "No se pudo registrar la función", 500)

    respuesta = {
        "id": id_creado,
        "pelicula_id": pelicula_id,
        "sala_id": sala_id,
        "mensaje": "Función programada con éxito",
    }
    return respuesta, None


def validar_qr_service(data):
    error = validar_datos_qr(data)
    if error:
        return None, error

    codigo_qr = data.get("codigo_qr")
    resultado_db = validar_y_marcar_qr_db(codigo_qr)

    if resultado_db is None:
        return None, ("INTERNAL_ERROR", "Error de base de datos", "No se pudo procesar la validación del QR", 500)

    if not resultado_db["valido"]:
        razon = resultado_db["razon"]
        mensaje = resultado_db["mensaje"]

        if razon == "NOT_FOUND":
            return None, ("NOT_FOUND", "QR Inválido", mensaje, 404)
        else:
            return None, ("CONFLICT", "Acceso Denegado", mensaje, 409)

    return {"valido": True, "mensaje": resultado_db["mensaje"]}, None


def obtener_dashboard_service(desde, hasta):
    error = validar_rango_fechas(desde, hasta)
    if error:
        return None, error

    metricas = obtener_metricas_dashboard_db(desde, hasta)

    if metricas is None:
        return None, ("INTERNAL_ERROR", "Error de base de datos", "No se pudieron obtener las métricas del dashboard", 500)

    respuesta = {
        "periodo": {
            "desde": desde,
            "hasta": hasta,
        },
        "metricas": {
            "total_compras": metricas["total_compras"],
            "facturacion_total": float(metricas["facturacion_total"]),
        },
    }
    return respuesta, None


def listar_salas_service():
    return listar_salas_db()