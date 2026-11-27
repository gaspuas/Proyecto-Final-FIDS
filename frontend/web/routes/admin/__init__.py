"""Autenticacion y rutas de la zona de administracion."""
from flask import Blueprint, abort, redirect, request, session, url_for

from frontend.web.utils.csrf import requerir_csrf
from frontend.web.routes.admin.peliculas import peliculas_bp
from frontend.web.routes.admin.novedades import novedades_bp

admin_bp = Blueprint('admin', __name__)


@admin_bp.before_request
def requerir_administrador():
    usuario = session.get('usuario')
    if not usuario:
        return redirect(url_for('web.site.login.index', next=request.path))
    if usuario.get('rol') != 'administrador':
        abort(403)
    # Novedades ya dispone de su propia validación CSRF en cada formulario.
    if (request.method == 'POST' and request.endpoint
            and request.endpoint.startswith('web.admin.peliculas.')):
        requerir_csrf()


@admin_bp.route('/')
def index():
    return redirect(url_for('web.admin.peliculas.index'))


admin_bp.register_blueprint(peliculas_bp, url_prefix='/peliculas')

admin_bp.register_blueprint(novedades_bp, url_prefix='/novedades')
