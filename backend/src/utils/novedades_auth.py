"""Autoriza operaciones de novedades únicamente a sesiones admin."""
from functools import wraps
from flask import jsonify, session


def admin_novedades_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        usuario = session.get('usuario')
        if not usuario:
            return jsonify({'error': 'Se requiere iniciar sesión.'}), 401
        if usuario.get('rol') != 'administrador':
            return jsonify({'error': 'Se requiere rol de administrador.'}), 403
        return fn(*args, **kwargs)
    return wrapper
