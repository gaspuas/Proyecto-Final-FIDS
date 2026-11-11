"""Seguridad fail-closed. Integrable con el sistema de roles definitivo."""
import os
from functools import wraps
from hmac import compare_digest
from flask import current_app, jsonify, request


def admin_novedades_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # Integración preferida: el backend inyecta su verificador de rol admin.
        authorizer = current_app.config.get("NOVEDADES_ADMIN_AUTHORIZER")
        if authorizer is not None:
            if not callable(authorizer):
                return jsonify({"error": "Configuración de seguridad inválida"}), 503
            if not authorizer():
                return jsonify({"error": "No autorizado"}), 403
            return fn(*args, **kwargs)

        # Alternativa temporal para pruebas de integración: token SECRETO explícito.
        # No hay token por defecto; si falta, las rutas admin quedan bloqueadas.
        secreto = os.environ.get("NOVEDADES_ADMIN_TOKEN", "")
        recibido = request.headers.get("X-Admin-Token", "")
        if not secreto or len(secreto) < 32:
            return jsonify({"error": "Administración no configurada"}), 503
        if not compare_digest(recibido, secreto):
            return jsonify({"error": "No autorizado"}), 403
        return fn(*args, **kwargs)
    return wrapper
