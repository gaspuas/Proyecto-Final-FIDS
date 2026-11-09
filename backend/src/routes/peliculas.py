from flask import Blueprint, request, jsonify
from backend.src.validators.peliculas_validators import *
from backend.src.services.peliculas_services import *
from backend.src.utils.api_responses import *

peliculas_bp = Blueprint('peliculas', __name__, url_prefix='/api/peliculas')

@peliculas_bp.route('', methods=['GET'])
def obtener_cartelera():
    # Obtener query params
    sede_id = request.args.get('sede_id')
    fecha = request.args.get('fecha')
    
    # Procesar petición a través del servicio
    resultado = procesar_obtener_cartelera(sede_id, fecha)
    
    if resultado['exito']:
        return jsonify({
            "status": "success",
            "data": resultado['datos']
        }), 200
    else:
        # Manejo de error de validación (400) o de base de datos/servidor (500)
        if  resultado.get('tipo_error') == 'VALIDATION':
            codigo_http = 400
        else:
            codigo_http = 500
        
        return generar_respuesta_error(
            code=resultado.get('tipo_error', 'INTERNAL_SERVER_ERROR'),
            message="Error al consultar la cartelera.",
            description=resultado['mensaje'],
            status_code=codigo_http
        )

@peliculas_bp.route('/<int:pelicula_id>', methods=['GET'])
def obtener_pelicula(pelicula_id):
    # Procesar petición a través del servicio siguiendo la convención de auth_services
    resultado = procesar_obtener_pelicula(pelicula_id)
    
    if resultado['exito']:
        return jsonify({
            "status": "success",
            "message": resultado['mensaje'],  # Homologado con el comportamiento de auth.py
            "data": resultado['datos']
        }), 200
    else:
        # Mapeo de códigos HTTP según el tipo de error
        if resultado.get('tipo_error') == 'NOT_FOUND':
            codigo_http = 404
        elif resultado.get('tipo_error') == 'VALIDATION':
            codigo_http = 400
        else:
            codigo_http = 500
            
        return generar_respuesta_error(
            code=resultado.get('tipo_error', 'INTERNAL_SERVER_ERROR'),
            message="Error al consultar el detalle de la película.",
            description=resultado['mensaje'],
            status_code=codigo_http
        )

@peliculas_bp.route('/<int:pelicula_id>/resenas', methods=['GET'])
def obtener_resenas_pelicula(pelicula_id: int):
    conexion = None
    try:
        conexion = get_db_connection()
        cursor = conexion.cursor(dictionary=True)

        # Hacemos JOIN con usuarios para obtener el nombre de quien reseñó
        query = """
            SELECT 
                r.id,
                r.usuario_id,
                u.nombre AS usuario_nombre,
                r.pelicula_id,
                r.compra_id,
                r.puntuacion,
                r.comentario,
                r.fecha
            FROM resenas r
            INNER JOIN usuarios u ON r.usuario_id = u.id
            WHERE r.pelicula_id = %s
            ORDER BY r.fecha DESC
        """
        cursor.execute(query, (pelicula_id,))
        resenas = cursor.fetchall()
        cursor.close()

        # Serializamos la fecha a formato string para JSON
        for r in resenas:
            if 'fecha' in r and r['fecha']:
                r['fecha'] = str(r['fecha'])
            # Aseguramos compatibilidad si el frontend busca 'calificacion' o 'puntuacion'
            r['calificacion'] = r['puntuacion']

        return jsonify(resenas), 200

    except Exception as e:
        print(f'Error al obtener reseñas en MySQL: {e}')
        return jsonify([]), 200
    finally:
        if conexion and conexion.is_connected():
            conexion.close()