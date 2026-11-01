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
        codigo_http = 400 if resultado.get('tipo_error') == 'VALIDATION' else 500
        
        return generar_respuesta_error(
            code=resultado.get('tipo_error', 'INTERNAL_SERVER_ERROR'),
            message="Error al consultar la cartelera.",
            description=resultado['mensaje'],
            status_code=codigo_http
        )