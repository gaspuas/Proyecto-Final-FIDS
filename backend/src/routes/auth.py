from flask import Blueprint, current_app, g, jsonify, request
import mysql.connector

from backend.src.services.auth_services import procesar_login, registrar_cliente_servicio
from backend.src.validators.auth_validators import validar_login, validar_registro
from backend.src.utils.api_responses import generar_respuesta_error
from backend.src.utils.token_auth import token_required
from backend.src.repositories.sesiones_repository import revocar_sesion

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
def registrar():
    data = request.get_json(silent=True)
    es_valido, mensaje_error = validar_registro(data)
    if not es_valido:
        return generar_respuesta_error(
            'VALIDATION_ERROR', 'Los datos proporcionados no son válidos.', mensaje_error, 400
        )
    try:
        exito = registrar_cliente_servicio(data)
        if not exito:
            return generar_respuesta_error(
                'EMAIL_ALREADY_EXISTS', 'Conflicto de registro.',
                'El email ingresado ya se encuentra registrado en el sistema.', 400,
            )
        return jsonify({'status': 'success', 'message': 'Usuario cliente registrado exitosamente.'}), 201
    except Exception:
        current_app.logger.exception('Error al registrar usuario')
        return generar_respuesta_error('INTERNAL_SERVER_ERROR', 'Error inesperado en el servidor.',
                                      'No se pudo registrar el usuario.', 500)


@auth_bp.route('/login', methods=['POST'])
def iniciar_sesion():
    data = request.get_json(silent=True)
    resultado = procesar_login(data)
    if resultado['exito']:
        return jsonify({'status': 'success', 'message': resultado['mensaje'], 'data': resultado['datos']}), 200
    error = resultado.get('tipo_error')
    status = 401 if error == 'UNAUTHORIZED' else (503 if error == 'SERVICE_UNAVAILABLE' else 400)
    return generar_respuesta_error(error or 'AUTH_ERROR', 'Error en la autenticación.',
                                  resultado['mensaje'], status)


@auth_bp.get('/me')
@token_required
def mi_sesion():
    return jsonify({'data': g.usuario}), 200


@auth_bp.post('/logout')
@token_required
def cerrar_sesion():
    try:
        revocar_sesion(g.token_hash)
    except mysql.connector.Error:
        current_app.logger.exception('No se pudo revocar TokenSession')
        return jsonify({'error': 'No se pudo cerrar la sesión en el backend.'}), 503
    return jsonify({'message': 'Sesión cerrada.'}), 200
