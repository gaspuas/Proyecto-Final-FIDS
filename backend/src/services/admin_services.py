from backend.src.repositories.admin_repository import insertar_pelicula_db
from backend.src.repositories.admin_repository import (
    insertar_pelicula_db, 
    insertar_funcion_db, 
    validar_y_marcar_qr_db,
    obtener_metricas_dashboard_db
)


def crear_pelicula_service(data):
    titulo = data.get('titulo')
    sinopsis = data.get('sinopsis')
    duracion = data.get('duracion') or data.get('duracion_minutos')
    poster_url = data.get('poster_url')
    
    
    if not titulo:
        return None, ("BAD_REQUEST", "Campo faltante", "El campo 'titulo' es obligatorio", 400)
    if not sinopsis:
        return None, ("BAD_REQUEST", "Campo faltante", "El campo 'sinopsis' es obligatorio", 400)
    if not duracion:
        return None, ("BAD_REQUEST", "Campo faltante", "El campo 'duracion' es obligatorio", 400)

    
    api_id = data.get('api_id')
    clasificacion = data.get('clasificacion')
    genero = data.get('genero')
    director = data.get('director')
    es_reestreno = data.get('es_reestreno', False)

    
    id_creado = insertar_pelicula_db(
        titulo=titulo,
        sinopsis=sinopsis,
        duracion_minutos=duracion,
        poster_url=poster_url,
        api_id=api_id,
        clasificacion=clasificacion,
        genero=genero,
        director=director,
        es_reestreno=es_reestreno
    )

    if not id_creado:
        return None, ("INTERNAL_ERROR", "Error de base de datos", "No se pudo registrar la película", 500)

    respuesta = {
        "id": id_creado,
        "titulo": titulo,
        "mensaje": "Película registrada con éxito"
    }
    return respuesta, None

from backend.src.repositories.admin_repository import insertar_pelicula_db, insertar_funcion_db

def crear_funcion_service(data):
    
    pelicula_id = data.get('id_pelicula') or data.get('pelicula_id')
    sala_id = data.get('id_sala') or data.get('sala_id')
    fecha_hora = data.get('fecha_hora')
    precio_base = data.get('precio') or data.get('precio_base')
    idioma = data.get('idioma', 'Español')
    formato = data.get('formato', '2D')

    
    if not pelicula_id:
        return None, ("BAD_REQUEST", "Campo faltante", "El campo 'id_pelicula' es obligatorio", 400)
    if not sala_id:
        return None, ("BAD_REQUEST", "Campo faltante", "El campo 'id_sala' es obligatorio", 400)
    if not fecha_hora:
        return None, ("BAD_REQUEST", "Campo faltante", "El campo 'fecha_hora' es obligatorio", 400)
    if precio_base is None:
        return None, ("BAD_REQUEST", "Campo faltante", "El campo 'precio' es obligatorio", 400)

   
    id_creado = insertar_funcion_db(
        pelicula_id=pelicula_id,
        sala_id=sala_id,
        fecha_hora=fecha_hora,
        precio_base=precio_base,
        idioma=idioma,
        formato=formato
    )

    if not id_creado:
        return None, ("INTERNAL_ERROR", "Error de base de datos", "No se pudo registrar la función", 500)

    respuesta = {
        "id": id_creado,
        "pelicula_id": pelicula_id,
        "sala_id": sala_id,
        "mensaje": "Función programada con éxito"
    }
    return respuesta, None

def validar_qr_service(data):
    codigo_qr = data.get('codigo_qr')

    if not codigo_qr:
        return None, ("BAD_REQUEST", "Campo faltante", "El campo 'codigo_qr' es obligatorio", 400)

    resultado_db = validar_y_marcar_qr_db(codigo_qr)

    if resultado_db is None:
        return None, ("INTERNAL_ERROR", "Error de base de datos", "No se pudo procesar la validación del QR", 500)

    
    if not resultado_db["valido"]:
        razon = resultado_db["razon"]
        mensaje = resultado_db["mensaje"]
        
        if razon == "NOT_FOUND":
            return None, ("NOT_FOUND", "QR Inválido", mensaje, 404)
        else: # ALREADY_USED o CANCELLED
            return None, ("CONFLICT", "Acceso Denegado", mensaje, 409)

    return {"valido": True, "mensaje": resultado_db["mensaje"]}, None

def obtener_dashboard_service(desde, hasta):
    if not desde or not hasta:
        return None, ("BAD_REQUEST", "Parámetros faltantes", "Los parámetros 'desde' y 'hasta' son obligatorios (ej. YYYY-MM-DD)", 400)

    metricas = obtener_metricas_dashboard_db(desde, hasta)

    if metricas is None:
        return None, ("INTERNAL_ERROR", "Error de base de datos", "No se pudieron obtener las métricas del dashboard", 500)

    respuesta = {
        "periodo": {
            "desde": desde,
            "hasta": hasta
        },
        "metricas": {
            "total_compras": metricas["total_compras"],
            "facturacion_total": float(metricas["facturacion_total"]),
            "total_entradas_vendidas": metricas["total_entradas_vendidas"]
        }
    }
    return respuesta, None