from flask import Blueprint, render_template
from web.services.peliculas import (
    obtener_peliculas,
    
)

peliculas_bp = Blueprint('peliculas', __name__)

@peliculas_bp.route('/')
def index():
    return render_template('admin/cartelera.html', peliculas=obtener_peliculas())

@peliculas_bp.route('/<int:pelicula_id>/editar', methods=['GET', 'POST'])
def editar():
    return render_template('admin/cartelera.html', peliculas=obtener_peliculas())

@peliculas_bp.route('/nueva', methods=['GET', 'POST'])
def nueva():
    return render_template('admin/cartelera.html', peliculas=obtener_peliculas())

@peliculas_bp.route('/<int:pelicula_id>/eliminar', methods=['POST'])
def eliminar():
    return render_template('admin/cartelera.html', peliculas=obtener_peliculas())