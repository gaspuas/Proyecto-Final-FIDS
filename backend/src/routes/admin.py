from flask import Blueprint, jsonify, request, session
from backend.src.utils.api_responses import generar_respuesta_error
from backend.src.services.admin_services import (
    crear_pelicula_service, 
    crear_funcion_service, 
    validar_qr_service,
    obtener_dashboard_service,
    listar_salas_service,
)
from backend.src.services.peliculas_services import procesar_listar_todas_las_peliculas

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


@admin_bp.before_request
def requerir_administrador():
    usuario = session.get('usuario')
    if not usuario:
        return jsonify({'error': 'Se requiere iniciar sesión.'}), 401
    if usuario.get('rol') != 'administrador':
        return jsonify({'error': 'Se requiere rol de administrador.'}), 403


@admin_bp.route('/salas', methods=['GET'])
def listar_salas():
    try:
        return jsonify({'data': listar_salas_service()}), 200
    except Exception as error:
        return generar_respuesta_error(
            'INTERNAL_SERVER_ERROR',
            'Error al consultar las salas.',
            str(error),
            500,
        )


@admin_bp.route('/peliculas', methods=['GET'])
def listar_todas_las_peliculas():
    resultado = procesar_listar_todas_las_peliculas()
    if resultado['exito']:
        return jsonify({'data': resultado['datos']}), 200
    return generar_respuesta_error(
        resultado.get('tipo_error', 'INTERNAL_SERVER_ERROR'),
        'Error al consultar las películas.',
        resultado['mensaje'],
        500,
    )

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