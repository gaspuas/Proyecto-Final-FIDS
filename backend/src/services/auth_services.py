from datetime import datetime, timedelta, timezone
from secrets import token_urlsafe

import mysql.connector
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash

from backend.src.repositories.auth_repository import crear_usuario_cliente, obtener_usuario_por_email
from backend.src.repositories.sesiones_repository import registrar_sesion
from backend.src.validators.auth_validators import validar_login


DURACION_TOKEN_HORAS = 2


def registrar_cliente_servicio(data):
    nombre = data.get('nombre')
    email = data.get('email')
    password = data.get('password')
    password_hash = generate_password_hash(password)
    return crear_usuario_cliente(
        nombre, email.strip(), password_hash,
        data['fecha_nacimiento'], data['recibir_promociones'],
    )


def procesar_login(data):
    es_valido, mensaje_error = validar_login(data)
    if not es_valido:
        return {'exito': False, 'mensaje': mensaje_error, 'tipo_error': 'VALIDATION'}

    usuario = obtener_usuario_por_email(data['email'])
    if not usuario or not check_password_hash(usuario['password_hash'], data['password']):
        return {'exito': False, 'mensaje': 'Credenciales inválidas.', 'tipo_error': 'UNAUTHORIZED'}

    token = token_urlsafe(32)
    expira_en = datetime.now(timezone.utc) + timedelta(hours=DURACION_TOKEN_HORAS)
    try:
        registrar_sesion(usuario['id'], token, expira_en)
    except mysql.connector.Error:
        current_app.logger.exception('No se pudo registrar TokenSession')
        return {
            'exito': False,
            'mensaje': 'No se pudo crear la sesión. Verificá que esté aplicada la migración 004.',
            'tipo_error': 'SERVICE_UNAVAILABLE',
        }

    datos_usuario = {
        'id': usuario['id'],
        'nombre': usuario['nombre'],
        'email': usuario['email'],
        'rol': usuario['rol'],
        'token': token,
        'expira_en': expira_en.isoformat(),
    }
    return {'exito': True, 'mensaje': 'Autenticación exitosa.', 'datos': datos_usuario}
