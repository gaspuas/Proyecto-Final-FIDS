"""Autorización centralizada de solicitudes API mediante TokenSession Bearer."""
import re
from functools import wraps
from hashlib import sha256

import mysql.connector
from flask import current_app, g, jsonify, request

from backend.src.repositories.sesiones_repository import buscar_usuario_por_token

_TOKEN_RE = re.compile(r'[A-Za-z0-9_-]{30,128}\Z')


def autorizar_token(rol_requerido=None):
    """Devuelve None si autorizó la solicitud; una respuesta HTTP si no."""
    authorization = request.headers.get('Authorization', '')
    partes = authorization.split()
    if len(partes) != 2 or partes[0].lower() != 'bearer' or not _TOKEN_RE.fullmatch(partes[1]):
        return jsonify({'error': 'Se requiere un token de sesión válido.'}), 401

    token = partes[1]
    try:
        usuario = buscar_usuario_por_token(token)
    except mysql.connector.Error:
        current_app.logger.exception('No se pudo validar TokenSession en MySQL')
        return jsonify({'error': 'No se pudo validar la sesión. Intentá más tarde.'}), 503

    if usuario is None:
        return jsonify({'error': 'Token vencido, revocado o inválido. Iniciá sesión nuevamente.'}), 401

    g.usuario = usuario
    g.token_hash = sha256(token.encode('utf-8')).hexdigest()
    if rol_requerido and usuario.get('rol') != rol_requerido:
        return jsonify({'error': 'Se requiere rol de administrador.'}), 403
    return None


def token_required(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        error = autorizar_token()
        if error is not None:
            return error
        return func(*args, **kwargs)
    return wrapped


def admin_token_required(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        error = autorizar_token('administrador')
        if error is not None:
            return error
        return func(*args, **kwargs)
    return wrapped
