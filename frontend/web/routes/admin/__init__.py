"""Autenticacion y rutas de la zona de administracion."""
from flask import Blueprint, abort, redirect, request, session, url_for

from frontend.web.routes.admin.peliculas import peliculas_bp

admin_bp = Blueprint('admin', __name__)


@admin_bp.before_request
def requerir_administrador():
    usuario = session.get('usuario')
    if not usuario:
        return redirect(url_for('web.site.login.index', next=request.path))
    if usuario.get('rol') != 'administrador':
        abort(403)


@admin_bp.route('/')
def index():
    return redirect(url_for('web.admin.peliculas.index'))


admin_bp.register_blueprint(peliculas_bp, url_prefix='/peliculas')
