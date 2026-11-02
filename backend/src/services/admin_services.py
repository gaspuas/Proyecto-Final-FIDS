from backend.src.repositories.admin_repository import insertar_pelicula_db

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