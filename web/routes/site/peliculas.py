from flask import Blueprint, render_template
from web.services.peliculas import (
    obtener_peliculas,
    
)

peliculas_bp = Blueprint('peliculas', __name__)

@peliculas_bp.route('/')
def index():
    return render_template('site/cartelera.html', peliculas=obtener_peliculas())
