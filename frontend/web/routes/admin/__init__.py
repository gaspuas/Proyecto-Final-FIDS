"""Blueprint padre para la zona de administracion (sin login, a proposito)."""
from flask import Blueprint, redirect, url_for

from frontend.web.routes.admin.peliculas import peliculas_bp
from frontend.web.sesion import verificar_admin

admin_bp = Blueprint('admin', __name__)

# Solo administradores en la capa web. La API /api/admin sigue sin autorizacion propia.
admin_bp.before_request(verificar_admin)


@admin_bp.route('/')
def index():
    return redirect(url_for('web.admin.peliculas.index'))


admin_bp.register_blueprint(peliculas_bp, url_prefix='/peliculas')
