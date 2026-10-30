"""Blueprint padre para la zona de administracion (sin login, a proposito)."""
from flask import Blueprint, redirect, url_for

from web.routes.admin.peliculas import peliculas_bp

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/')
def index():
    return redirect(url_for('web.admin.peliculas.index'))


admin_bp.register_blueprint(peliculas_bp, url_prefix='/peliculas')
