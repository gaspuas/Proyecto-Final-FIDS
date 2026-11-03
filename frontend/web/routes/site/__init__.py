"""Blueprint padre para la zona publica del sitio."""
from flask import Blueprint

from frontend.web.routes.site.compra import compra_bp
from frontend.web.routes.site.home import home_bp
from frontend.web.routes.site.login import login_bp
from frontend.web.routes.site.peliculas import peliculas_bp
from frontend.web.routes.site.reserva import reserva_bp

site_bp = Blueprint('site', __name__)

site_bp.register_blueprint(home_bp)
site_bp.register_blueprint(login_bp)
site_bp.register_blueprint(compra_bp, url_prefix='/compra')
site_bp.register_blueprint(peliculas_bp, url_prefix='/peliculas')
site_bp.register_blueprint(reserva_bp, url_prefix='/reserva')
