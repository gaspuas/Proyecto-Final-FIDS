from io import BytesIO
from pathlib import Path
from uuid import uuid4
from urllib.parse import urlparse
from flask import current_app, session
from PIL import Image, UnidentifiedImageError
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from frontend.web.services.api_client import BackendAPIError
from frontend.web.services.admin import obtener_salas
from frontend.web.services.peliculas import (
    crear_funcion,
    crear_pelicula,
    obtener_todas_las_peliculas,
    actualizar_poster_pelicula,
    obtener_pelicula,
)

peliculas_bp = Blueprint('peliculas', __name__)


def _guardar_imagen_funcion(archivo, carpeta="funciones"):
    """Guarda una copia WEBP; no reemplaza los pósters originales."""
    if not archivo or not archivo.filename:
        return None
    if Path(archivo.filename).suffix.lower() not in {'.jpg', '.jpeg', '.png', '.webp'}:
        raise ValueError('La imagen debe ser JPG, PNG o WebP.')
    data = archivo.stream.read(5 * 1024 * 1024 + 1)
    if len(data) > 5 * 1024 * 1024:
        raise ValueError('La imagen supera los 5 MB.')
    try:
        with Image.open(BytesIO(data)) as picture:
            if picture.width * picture.height > 20_000_000:
                raise ValueError('La imagen supera los 20 megapíxeles.')
            picture.load()
            if picture.format not in {'JPEG', 'PNG', 'WEBP'}:
                raise ValueError('Formato de imagen inválido.')
            result = picture.convert('RGB')
            if result.width > 2200:
                result = result.resize((2200, round(result.height * 2200 / result.width)), Image.Resampling.LANCZOS)
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
        raise ValueError('La imagen no es válida.') from exc
    folder = Path(current_app.static_folder) / 'img' / carpeta
    folder.mkdir(parents=True, exist_ok=True)
    name = f'{uuid4().hex}.webp'
    result.save(folder / name, format='WEBP', quality=88)
    return url_for('static', filename=f'img/{carpeta}/{name}')



def _imagenes_del_proyecto():
    """Biblioteca de imágenes para los formularios. No duplica los archivos."""
    grupos = []
    raiz = Path(current_app.static_folder) / 'img'
    for carpeta, titulo in (('novedades', 'Promociones'), ('peliculas', 'Películas'), ('funciones', 'Funciones')):
        encontrados = []
        directorio = raiz / carpeta
        if directorio.is_dir():
            for archivo in sorted(directorio.iterdir(), key=lambda f: f.name.casefold()):
                if archivo.is_file() and archivo.suffix.lower() in {'.jpg', '.jpeg', '.png', '.webp', '.svg'}:
                    encontrados.append({'nombre': archivo.stem.replace('_', ' '), 'url': url_for('static', filename=f'img/{carpeta}/{archivo.name}')})
        grupos.append({'titulo': titulo, 'imagenes': encontrados})
    return grupos


def _imagen_existente(url, grupos):
    validas = {item['url'] for grupo in grupos for item in grupo['imagenes']}
    if url not in validas:
        raise ValueError('Seleccioná una imagen existente de la lista.')
    return url


def _validar_url_imagen(url):
    if not url:
        return None
    parsed = urlparse(url)
    if (parsed.scheme in {'https', 'http'} and parsed.netloc) or (url.startswith('/static/img/') and '..' not in url and not url.startswith('//')):
        return url
    raise ValueError('La URL de imagen debe ser http(s) o una ruta local /static/img/.')


def _resolver_imagen(carpeta, grupos, *, imagen_por_defecto=None):
    """Prioridad: archivo subido > existente > URL > póster por defecto."""
    archivo = request.files.get('imagen_archivo')
    # Si aplicó el encuadre, la imagen WebP debe llegar efectivamente al servidor.
    # No caer silenciosamente a la URL original o a otra imagen del selector.
    if request.form.get('encuadre_aplicado') == '1':
        if not archivo or not archivo.filename or Path(archivo.filename).suffix.lower() != '.webp':
            raise ValueError('El encuadre no llegó al servidor. Aplicá el recorte otra vez antes de guardar.')
    if archivo and archivo.filename:
        return _guardar_imagen_funcion(archivo, carpeta=carpeta)
    elegida = request.form.get('imagen_existente', '').strip()
    if elegida:
        return _imagen_existente(elegida, grupos)
    url = request.form.get('imagen_url_manual', '').strip()
    if url:
        return _validar_url_imagen(url)
    return imagen_por_defecto


@peliculas_bp.route('/')
def index():
    return render_template(
        'admin/cartelera.html',
        peliculas=obtener_todas_las_peliculas(),
    )


@peliculas_bp.route('/nueva', methods=['GET', 'POST'])
def nueva():
    grupos = _imagenes_del_proyecto()
    if request.method == 'POST':
        try:
            poster = _resolver_imagen('peliculas', grupos)
            datos = {
                'titulo': request.form.get('titulo', '').strip(),
                'sinopsis': request.form.get('sinopsis', '').strip(),
                'duracion_minutos': request.form.get('duracion_minutos', type=int),
                'poster_url': poster,
                'clasificacion': request.form.get('clasificacion', '').strip() or None,
                'genero': request.form.get('genero', '').strip() or None,
                'director': request.form.get('director', '').strip() or None,
                'es_reestreno': request.form.get('es_reestreno') == 'on',
            }
            respuesta = crear_pelicula(datos)
            if poster and isinstance(respuesta, dict) and respuesta.get('id'):
                pelicula_guardada = obtener_pelicula(respuesta['id'])
                if pelicula_guardada.get('poster_url') != poster:
                    raise ValueError('La API no confirmó la imagen de la película en Cartelera.')
        except (BackendAPIError, ValueError) as error:
            return render_template('admin/nueva_pelicula.html', error=str(error), grupos_imagenes=grupos), 400 if isinstance(error, ValueError) else (error.status_code if 400 <= error.status_code < 500 else 503)
        flash('La película se creó correctamente.', 'success')
        return redirect(url_for('.index'))
    return render_template('admin/nueva_pelicula.html', grupos_imagenes=grupos)




@peliculas_bp.route('/<int:pelicula_id>/poster', methods=['GET', 'POST'])
def editar_poster(pelicula_id):
    """Actualiza el póster de una película ya creada; no altera sus funciones."""
    peliculas = obtener_todas_las_peliculas()
    pelicula = next((p for p in peliculas if int(p['id']) == pelicula_id), None)
    if pelicula is None:
        abort(404)
    grupos = _imagenes_del_proyecto()
    if request.method == 'POST':
        try:
            imagen = _resolver_imagen(
                'peliculas', grupos, imagen_por_defecto=pelicula.get('poster_url')
            )
            if not imagen:
                raise ValueError('Elegí una imagen y aplicá su encuadre.')
            actualizar_poster_pelicula(pelicula_id, imagen)
            # Confirmar contra la API pública, que es exactamente la fuente de /peliculas/.
            pelicula_guardada = obtener_pelicula(pelicula_id)
            if pelicula_guardada.get('poster_url') != imagen:
                raise ValueError('La API no devolvió el nuevo póster. No se confirmó el guardado en Cartelera.')
        except (BackendAPIError, ValueError) as error:
            estado = 400 if isinstance(error, ValueError) else (error.status_code if 400 <= error.status_code < 500 else 503)
            return render_template('admin/editar_poster_pelicula.html',
                                   pelicula=pelicula, grupos_imagenes=grupos,
                                   error=str(error)), estado
        flash('Se actualizó el póster de la película en Cartelera.', 'success')
        return redirect(url_for('web.admin.peliculas.index'))
    return render_template('admin/editar_poster_pelicula.html',
                           pelicula=pelicula, grupos_imagenes=grupos)

@peliculas_bp.route('/funciones/nueva', methods=['GET', 'POST'])
def nueva_funcion():
    peliculas = obtener_todas_las_peliculas()
    salas = obtener_salas()
    grupos = _imagenes_del_proyecto()
    if request.method == 'POST':
        fecha_hora = request.form.get('fecha_hora', '').replace('T', ' ')
        try:
            imagen = _resolver_imagen('funciones', grupos)
            crear_funcion({
                'imagen_url': imagen,
                'pelicula_id': request.form.get('pelicula_id', type=int),
                'sala_id': request.form.get('sala_id', type=int),
                'fecha_hora': fecha_hora,
                'precio_base': request.form.get('precio_base', type=float),
                'idioma': request.form.get('idioma', 'Español').strip(),
                'formato': request.form.get('formato', '2D').strip(),
            })
        except (BackendAPIError, ValueError) as error:
            return render_template(
                'admin/nueva_funcion.html',
                peliculas=peliculas,
                salas=salas,
                grupos_imagenes=grupos,
                error=str(error),
            ), 400 if isinstance(error, ValueError) else (error.status_code if 400 <= error.status_code < 500 else 503)
        flash('La función se programó correctamente.', 'success')
        return redirect(url_for('web.admin.peliculas.index'))

    return render_template('admin/nueva_funcion.html', peliculas=peliculas, salas=salas, grupos_imagenes=grupos)
