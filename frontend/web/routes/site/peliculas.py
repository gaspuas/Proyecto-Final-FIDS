from flask import Blueprint, render_template, request

from frontend.web.services.funciones import obtener_funciones
from frontend.web.services.peliculas import (
    obtener_pelicula,
    obtener_peliculas,
    obtener_resenas,
)

peliculas_bp = Blueprint('peliculas', __name__)


@peliculas_bp.route('/')
def index():
    peliculas = obtener_peliculas(
        sede_id=request.args.get('sede_id'),
        fecha=request.args.get('fecha'),
    )
    return render_template('site/cartelera.html', peliculas=peliculas)


@peliculas_bp.route('/pelicula/<int:pelicula_id>')
def detalle(pelicula_id):
    pelicula = obtener_pelicula(pelicula_id)
    return render_template(
        'site/pelicula_detalle.html',
        pelicula=pelicula,
        funciones=obtener_funciones(pelicula_id),
        resenas=obtener_resenas(pelicula_id),
    )
