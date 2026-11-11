from flask import Blueprint, flash, redirect, render_template, request, url_for

from frontend.web.services import auth
from frontend.web.services.api import ErrorApi
from frontend.web.sesion import (
    cerrar_sesion,
    csrf_requerido,
    destino_seguro,
    es_admin,
    iniciar_sesion,
    token_csrf,
    usuario_actual,
)

login_bp = Blueprint('login', __name__)


@login_bp.app_context_processor
def contexto_sesion():
    """Datos de sesion disponibles en todas las plantillas (navbar y formularios)."""
    usuario = usuario_actual()
    return {
        'usuario_sesion': usuario,
        'usuario_es_admin': es_admin(usuario),
        'csrf_token': token_csrf,
    }


def _destino():
    return destino_seguro(request.values.get('next'), url_for('web.site.home.index'))


def _render_login(status=200, **errores):
    siguiente = destino_seguro(request.values.get('next'), None)
    return render_template(
        'site/login.html', next=siguiente, form=request.form, **errores
    ), status


@login_bp.route('/login', methods=['GET', 'POST'])
def index():
    if usuario_actual() is not None:
        return redirect(_destino())
    if request.method == 'GET':
        return _render_login()
    return _procesar_login()


@csrf_requerido
def _procesar_login():
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')
    if not email or not password:
        return _render_login(400, error_login='Completá tu email y tu contraseña.')

    try:
        usuario = auth.autenticar(email, password)
    except ErrorApi as error:
        return _render_login(error.status or 503, error_login=error.mensaje)

    iniciar_sesion(usuario)
    flash(f"¡Hola, {usuario['nombre']}!", 'success')
    return redirect(_destino())


@login_bp.route('/registro', methods=['POST'])
@csrf_requerido
def registro():
    nombre = request.form.get('nombre', '').strip()
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')
    if not nombre or not email or len(password) < 6:
        return _render_login(
            400,
            error_registro='Completá nombre, email y una contraseña de al menos 6 caracteres.',
        )

    try:
        auth.registrar(nombre, email, password)
    except ErrorApi as error:
        return _render_login(error.status or 503, error_registro=error.mensaje)

    # La API de registro no devuelve el usuario: se inicia sesion con los mismos datos
    try:
        usuario = auth.autenticar(email, password)
    except ErrorApi:
        flash('Tu cuenta se creó. Ingresá con tu email y contraseña.', 'success')
        return redirect(url_for('web.site.login.index', next=destino_seguro(request.values.get('next'), None)))

    iniciar_sesion(usuario)
    flash(f"¡Bienvenido/a, {usuario['nombre']}! Tu cuenta se creó correctamente.", 'success')
    return redirect(_destino())


@login_bp.route('/logout', methods=['POST'])
@csrf_requerido
def logout():
    cerrar_sesion()
    flash('Cerraste sesión.', 'success')
    return redirect(url_for('web.site.home.index'))
