"""Blueprint padre para la zona publica del sitio."""
from flask import Blueprint

from web.routes.site.compra import compra_bp
from web.routes.site.home import home_bp
from web.routes.site.login import login_bp
from web.routes.site.peliculas import peliculas_bp

site_bp = Blueprint('site', __name__)

site_bp.register_blueprint(home_bp)
site_bp.register_blueprint(login_bp)
site_bp.register_blueprint(compra_bp, url_prefix='/compra')
site_bp.register_blueprint(peliculas_bp, url_prefix='/peliculas')
