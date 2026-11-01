from flask import Blueprint, request, jsonify
from backend.src.validators.auth_validators import *
from backend.src.services.auth_services import *
from backend.src.utils.api_responses import *

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def registrar():
    data = request.get_json(silent=True)

    es_valido, mensaje_error = validar_registro(data)
    if not es_valido:
        return generar_respuesta_error(
            code="VALIDATION_ERROR",
            message="Los datos proporcionados no son válidos.",
            description=mensaje_error,
            status_code=400
        )

    try:
        exito = registrar_cliente_servicio(data)
        if not exito:
            return generar_respuesta_error(
                code="EMAIL_ALREADY_EXISTS",
                message="Conflicto de registro.",
                description="El email ingresado ya se encuentra registrado en el sistema.",
                status_code=400
            )
            
        return jsonify({
            "status": "success",
            "message": "Usuario cliente registrado exitosamente."
        }), 201
        
    except Exception as e:
        return generar_respuesta_error(
            code="INTERNAL_SERVER_ERROR",
            message="Error inesperado en el servidor.",
            description=str(e),
            status_code=500
        )

@auth_bp.route('/login', methods=['POST'])
def iniciar_sesion():
    data = request.get_json(silent=True)
    
    resultado = procesar_login(data)
    
    if resultado['exito']:
        return jsonify({
            "status": "success",
            "message": resultado['mensaje'],
            "data": resultado['datos']
        }), 200
    else:
        codigo_http = 401 if resultado.get('tipo_error') == 'UNAUTHORIZED' else 400
        
        return generar_respuesta_error(
            code=resultado.get('tipo_error', 'AUTH_ERROR'),
            message="Error en la autenticación.",
            description=resultado['mensaje'],
            status_code=codigo_http
        )