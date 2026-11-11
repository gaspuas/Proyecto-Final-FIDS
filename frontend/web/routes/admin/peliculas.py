from flask import Blueprint, flash, redirect, render_template, request, url_for

from frontend.web.services.api_client import BackendAPIError
from frontend.web.services.admin import obtener_salas
from frontend.web.services.peliculas import (
    crear_funcion,
    crear_pelicula,
    obtener_todas_las_peliculas,
)

peliculas_bp = Blueprint('peliculas', __name__)


@peliculas_bp.route('/')
def index():
    return render_template(
        'admin/cartelera.html',
        peliculas=obtener_todas_las_peliculas(),
    )


@peliculas_bp.route('/nueva', methods=['GET', 'POST'])
def nueva():
    if request.method == 'POST':
        datos = {
            'titulo': request.form.get('titulo', '').strip(),
            'sinopsis': request.form.get('sinopsis', '').strip(),
            'duracion_minutos': request.form.get('duracion_minutos', type=int),
            'poster_url': request.form.get('poster_url', '').strip() or None,
            'clasificacion': request.form.get('clasificacion', '').strip() or None,
            'genero': request.form.get('genero', '').strip() or None,
            'director': request.form.get('director', '').strip() or None,
            'es_reestreno': request.form.get('es_reestreno') == 'on',
        }
        try:
            crear_pelicula(datos)
        except BackendAPIError as error:
            return render_template(
                'admin/nueva_pelicula.html',
                error=str(error),
            ), error.status_code if 400 <= error.status_code < 500 else 503
        flash('La película se creó correctamente.', 'success')
        return redirect(url_for('.index'))

    return render_template('admin/nueva_pelicula.html')


@peliculas_bp.route('/funciones/nueva', methods=['GET', 'POST'])
def nueva_funcion():
    peliculas = obtener_todas_las_peliculas()
    salas = obtener_salas()
    if request.method == 'POST':
        fecha_hora = request.form.get('fecha_hora', '').replace('T', ' ')
        try:
            crear_funcion({
                'pelicula_id': request.form.get('pelicula_id', type=int),
                'sala_id': request.form.get('sala_id', type=int),
                'fecha_hora': fecha_hora,
                'precio_base': request.form.get('precio_base', type=float),
                'idioma': request.form.get('idioma', 'Español').strip(),
                'formato': request.form.get('formato', '2D').strip(),
            })
        except BackendAPIError as error:
            return render_template(
                'admin/nueva_funcion.html',
                peliculas=peliculas,
                salas=salas,
                error=str(error),
            ), error.status_code if 400 <= error.status_code < 500 else 503
        flash('La función se programó correctamente.', 'success')
        return redirect(url_for('web.admin.peliculas.index'))

    return render_template('admin/nueva_funcion.html', peliculas=peliculas, salas=salas)
