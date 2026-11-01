from flask import Blueprint, request, jsonify
from backend.src.validators.auth_validators import *
from backend.src.services.auth_services import *
from backend.src.utils.api_responses import *

# Definición del Blueprint para las rutas de autenticación
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    # Obtener el Body: {nombre, email, password}
    data = request.get_json(silent=True)

    # 1. Validar la entrada
    es_valido, mensaje_error = validar_registro(data)
    if not es_valido:
        # Se utiliza el helper del archivo api_responses.py para el 400 Bad Request
        return generar_respuesta_error(
            code="VALIDATION_ERROR",
            message="Los datos proporcionados no son válidos.",
            description=mensaje_error,
            status_code=400
        )

    # 2. Procesar el registro (Llamada al servicio)
    try:
        exito = registrar_cliente_service(data)
        if not exito:
            return generar_respuesta_error(
                code="EMAIL_ALREADY_EXISTS",
                message="Conflicto de registro.",
                description="El email ingresado ya se encuentra registrado en el sistema.",
                status_code=400
            )
            
        # Retorna 201 Created para el caso de éxito
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