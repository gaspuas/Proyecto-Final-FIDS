from flask import Blueprint, render_template
from frontend.web.services.novedades import obtener_novedades

home_bp = Blueprint('home', __name__)


@home_bp.route('/')
def index():
    # PENDIENTE BACKEND: /api/novedades. Si aún no está, se muestra el
    # estado sin novedades y el resto de la home sigue funcionando.
    novedades = obtener_novedades()
    return render_template('site/inicio.html', novedades=novedades)
