"""ABM de novedades. Subidas al disco local del frontend, API en backend."""
import secrets
from datetime import datetime
from email.utils import parsedate_to_datetime
from io import BytesIO
from pathlib import Path
from uuid import uuid4
from urllib.parse import quote

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, session, url_for
from PIL import Image, UnidentifiedImageError

from frontend.web.services.admin_novedades import (
    listar_novedades_admin, crear_novedad, editar_novedad, eliminar_novedad,
)
from frontend.web.services.api_client import BackendAPIError

novedades_bp = Blueprint('novedades', __name__)
MAX_UPLOAD_BYTES = 5 * 1024 * 1024
MAX_IMAGE_PIXELS = 20_000_000


def _csrf():
    if 'admin_novedades_csrf' not in session:
        session['admin_novedades_csrf'] = secrets.token_urlsafe(32)
    return session['admin_novedades_csrf']


def _require_csrf():
    if not secrets.compare_digest(request.form.get('csrf_token', ''), session.get('admin_novedades_csrf', '')):
        abort(400, 'Formulario inválido. Recargá la página e intentá nuevamente.')


def _subir_imagen(archivo):
    if not archivo or not archivo.filename:
        return None
    if Path(archivo.filename).suffix.lower() not in {'.jpg', '.jpeg', '.png', '.webp'}:
        raise ValueError('La imagen debe ser JPG, PNG o WebP.')
    raw = archivo.stream.read(MAX_UPLOAD_BYTES + 1)
    if len(raw) > MAX_UPLOAD_BYTES:
        raise ValueError('La imagen supera el límite de 5 MB.')
    try:
        with Image.open(BytesIO(raw)) as image:
            if image.width * image.height > MAX_IMAGE_PIXELS:
                raise ValueError('La imagen es demasiado grande (máximo 20 megapíxeles).')
            image.load()
            if image.format not in {'JPEG', 'PNG', 'WEBP'}:
                raise ValueError('La imagen debe ser JPG, PNG o WebP.')
            procesada = image.convert('RGB')
            if procesada.width > 2200:
                height = round(procesada.height * 2200 / procesada.width)
                procesada = procesada.resize((2200, height), Image.Resampling.LANCZOS)
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
        raise ValueError('El archivo no es una imagen válida.') from exc
    destino = Path(current_app.static_folder) / 'img' / 'novedades'
    destino.mkdir(parents=True, exist_ok=True)
    nombre = f'{uuid4().hex}.webp'
    procesada.save(destino / nombre, format='WEBP', quality=88)
    return url_for('static', filename=f'img/novedades/{nombre}')


def _imagenes_disponibles():
    """Lista de imágenes ya existentes en el repositorio, sin duplicarlas."""
    raiz = Path(current_app.static_folder) / 'img'
    grupos = []
    for carpeta, titulo in (('novedades', 'Promociones'), ('peliculas', 'Películas')):
        directorio = raiz / carpeta
        imagenes = []
        if directorio.is_dir():
            for archivo in sorted(directorio.iterdir(), key=lambda p: p.name.casefold()):
                if archivo.is_file() and archivo.suffix.lower() in {'.jpg', '.jpeg', '.png', '.webp', '.svg'}:
                    imagenes.append({
                        'nombre': archivo.stem.replace('_', ' '),
                        'url': url_for('static', filename=f'img/{carpeta}/{archivo.name}'),
                    })
        grupos.append({'titulo': titulo, 'imagenes': imagenes})
    return grupos


def _validar_imagen_existente(url):
    disponibles = {foto['url'] for grupo in _imagenes_disponibles() for foto in grupo['imagenes']}
    if url not in disponibles:
        raise ValueError('Seleccioná una imagen existente de la lista.')
    return url


def _datos_formulario(imagen_previa=None):
    titulo = request.form.get('titulo', '').strip()
    tipo = request.form.get('tipo', 'oferta').strip()
    enlace = request.form.get('enlace', '').strip()
    imagen_url = imagen_previa
    elegida = request.form.get('imagen_existente', '').strip()
    if elegida:
        imagen_url = _validar_imagen_existente(elegida)
    archivo = request.files.get('imagen_archivo')
    if archivo and archivo.filename:
        imagen_url = _subir_imagen(archivo)
    if not imagen_url:
        raise ValueError('Seleccioná una imagen del proyecto o subí una desde tu computadora.')
    try:
        orden = int(request.form.get('orden', '0'))
    except ValueError as exc:
        raise ValueError('El orden debe ser un número entero.') from exc
    if orden < 0:
        raise ValueError('El orden no puede ser negativo.')
    datos = {
        'titulo': titulo,
        'descripcion': request.form.get('descripcion', '').strip(),
        'imagen_url': imagen_url,
        'tipo': tipo,
        'enlace': enlace or None,
        'orden': orden,
        'activo': request.form.get('activo') == 'on',
        'fecha_inicio': request.form.get('fecha_inicio', '').strip() or None,
        'fecha_fin': request.form.get('fecha_fin', '').strip() or None,
    }
    return datos


def _fecha_input(valor):
    if not valor:
        return ''
    if isinstance(valor, datetime):
        return valor.strftime('%Y-%m-%dT%H:%M')
    try:
        return parsedate_to_datetime(str(valor)).strftime('%Y-%m-%dT%H:%M')
    except (ValueError, TypeError, IndexError):
        return str(valor).replace(' ', 'T')[:16]


def _render_formulario(novedad=None, error=None, status=200):
    return render_template('admin/novedad_form.html', novedad=novedad,
                           error=error, csrf_token=_csrf(), fecha_input=_fecha_input,
                           grupos_imagenes=_imagenes_disponibles()), status


@novedades_bp.get('/')
def index():
    return render_template('admin/novedades.html', novedades=listar_novedades_admin(),
                           csrf_token=_csrf())


@novedades_bp.route('/nueva', methods=['GET', 'POST'])
def nueva():
    if request.method == 'POST':
        _require_csrf()
        try:
            crear_novedad(_datos_formulario())
        except (ValueError, BackendAPIError) as error:
            return _render_formulario(error=str(error), status=400 if isinstance(error, ValueError) else error.status_code)
        flash('Novedad creada correctamente.', 'success')
        return redirect(url_for('.index'))
    return _render_formulario()


@novedades_bp.route('/<int:novedad_id>/editar', methods=['GET', 'POST'])
def editar(novedad_id):
    novedades = listar_novedades_admin()
    novedad = next((item for item in novedades if item.get('id') == novedad_id), None)
    if not novedad:
        abort(404)
    if request.method == 'POST':
        _require_csrf()
        try:
            editar_novedad(novedad_id, _datos_formulario(imagen_previa=novedad.get('imagen_url')))
        except (ValueError, BackendAPIError) as error:
            return _render_formulario(novedad, str(error), 400 if isinstance(error, ValueError) else error.status_code)
        flash('Novedad actualizada correctamente.', 'success')
        return redirect(url_for('.index'))
    return _render_formulario(novedad)


@novedades_bp.post('/<int:novedad_id>/eliminar')
def eliminar(novedad_id):
    _require_csrf()
    eliminar_novedad(novedad_id)
    flash('Novedad eliminada.', 'success')
    return redirect(url_for('.index'))
