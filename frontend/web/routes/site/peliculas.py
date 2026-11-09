import requests
from flask import Blueprint, abort, current_app, render_template, request
from frontend.web.services.peliculas import obtener_peliculas

peliculas_bp = Blueprint('peliculas', __name__)


def _obtener_funciones_por_pelicula(pelicula_id):
    api_url = current_app.config.get('API_URL', 'http://127.0.0.1:5000')
    try:
        res = requests.get(f'{api_url}/api/funciones?pelicula_id={pelicula_id}', timeout=3)
        print("STATUS API FUNCIONES:", res.status_code)
        print("DATOS RECIBIDOS:", res.json())
        
        if res.status_code == 200:
            datos = res.json()
            # Si el backend devuelve un dict tipo {"funciones": [...]}, extraemos la lista
            if isinstance(datos, dict):
                return datos.get('funciones', [])
            return datos
    except Exception as e:
        print(f"Error al obtener funciones para la película {pelicula_id}: {e}")

    return []


def _obtener_resenas_por_pelicula(pelicula_id):
    api_url = current_app.config.get('API_URL', 'http://127.0.0.1:5000')
    try:
        res = requests.get(
            f'{api_url}/api/peliculas/{pelicula_id}/resenas', timeout=3
        )
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        print(f'Error al obtener reseñas para la película {pelicula_id}: {e}')
    return []

@peliculas_bp.route('/')
def index():
    """Vista principal de la cartelera de películas."""
    peliculas = obtener_peliculas(
        sede_id=request.args.get('sede_id'),
        fecha=request.args.get('fecha'),
    )
    return render_template('site/cartelera.html', peliculas=peliculas)

@peliculas_bp.route('/pelicula/<int:pelicula_id>')
def detalle(pelicula_id):
    pelicula = next(
        (
            pelicula
            for pelicula in obtener_peliculas()
            if pelicula['id'] == pelicula_id
        ),
        None,
    )
    if pelicula is None:
        abort(404)

    # Obtenemos funciones y reseñas reales cargadas en MySQL
    funciones_reales = _obtener_funciones_por_pelicula(pelicula_id)
    resenas_reales = _obtener_resenas_por_pelicula(pelicula_id)
    if isinstance(funciones_reales, dict):
        funciones_reales = funciones_reales.get('funciones', [])

    return render_template(
        'site/pelicula_detalle.html',
        pelicula=pelicula,
        funciones=funciones_reales,
        resenas=resenas_reales,  # <-- ¡Reemplazado RESENAS_DEMO!
    )