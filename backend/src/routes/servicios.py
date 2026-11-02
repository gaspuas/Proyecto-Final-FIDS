from flask import Blueprint, jsonify
from backend.src.services.servicios_services import *
from backend.src.utils.api_responses import *

servicios_bp = Blueprint('servicios', __name__, url_prefix='/api/servicios')


@servicios_bp.route('', methods=['GET'])
def obtener_servicios():
    resultado = procesar_listar_servicios()

    if resultado['exito']:
        return jsonify({
            "status": "success",
            "message": resultado['mensaje'],
            "data": resultado['datos']
        }), 200

    return generar_respuesta_error(
        code=resultado.get('tipo_error', 'INTERNAL_SERVER_ERROR'),
        message="Error al consultar los servicios.",
        description=resultado['mensaje'],
        status_code=500
    )
