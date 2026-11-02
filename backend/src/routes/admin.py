from flask import Blueprint, request, jsonify
from backend.src.utils.api_responses import generar_respuesta_error
from backend.src.services.admin_services import (
    crear_pelicula_service, 
    crear_funcion_service, 
    validar_qr_service,
    obtener_dashboard_service
)

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@admin_bp.route('/peliculas', methods=['POST'])
def alta_pelicula():
    data = request.get_json()
    
    if not data:
        return generar_respuesta_error(
            code="INVALID_JSON",
            message="Cuerpo inválido",
            description="La petición debe ser un JSON válido",
            status_code=400
        )

    resultado, error = crear_pelicula_service(data)

    if error:
        code, message, description, status_code = error
        return generar_respuesta_error(code, message, description, status_code)

    return jsonify(resultado), 201

@admin_bp.route('/funciones', methods=['POST'])
def alta_funcion():
    data = request.get_json()
    
    if not data:
        return generar_respuesta_error(
            code="INVALID_JSON",
            message="Cuerpo inválido",
            description="La petición debe ser un JSON válido",
            status_code=400
        )

    resultado, error = crear_funcion_service(data)

    if error:
        code, message, description, status_code = error
        return generar_respuesta_error(code, message, description, status_code)

    return jsonify(resultado), 201

@admin_bp.route('/validar-qr', methods=['POST'])
def validar_qr():
    data = request.get_json()
    
    if not data:
        return generar_respuesta_error(
            code="INVALID_JSON",
            message="Cuerpo inválido",
            description="La petición debe ser un JSON válido",
            status_code=400
        )

    resultado, error = validar_qr_service(data)

    if error:
        code, message, description, status_code = error
        return generar_respuesta_error(code, message, description, status_code)

    return jsonify(resultado), 200

@admin_bp.route('/dashboard', methods=['GET'])
def get_dashboard():
    desde = request.args.get('desde')
    hasta = request.args.get('hasta')

    resultado, error = obtener_dashboard_service(desde, hasta)

    if error:
        code, message, description, status_code = error
        return generar_respuesta_error(code, message, description, status_code)

    return jsonify(resultado), 200