from flask import Blueprint, abort, render_template, request

from frontend.web.constants import FUNCIONES_DEMO, RESENAS_DEMO
from frontend.web.services.peliculas import obtener_peliculas

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
    pelicula = next(
        (pelicula for pelicula in obtener_peliculas() if pelicula['id'] == pelicula_id),
        None,
    )
    if pelicula is None:
        abort(404)

    return render_template(
        'site/pelicula_detalle.html',
        pelicula=pelicula,
        funciones=FUNCIONES_DEMO,
        resenas=RESENAS_DEMO,
    )
