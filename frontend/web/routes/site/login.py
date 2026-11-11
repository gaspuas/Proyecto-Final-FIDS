from urllib.parse import urlparse

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from frontend.web.services.api_client import BackendAPIError
from frontend.web.services.autenticacion import iniciar_sesion, registrar_usuario

login_bp = Blueprint('login', __name__)


def _safe_next_url(value):
    if not value:
        return None
    parsed = urlparse(value)
    if parsed.scheme or parsed.netloc or not value.startswith('/'):
        return None
    return value


@login_bp.route('/login', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        accion = request.form.get('accion')
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        try:
            if accion == 'registro':
                registrar_usuario(
                    request.form.get('nombre', '').strip(),
                    email,
                    password,
                )
                flash('Tu cuenta fue creada. Ya podés iniciar sesión.', 'success')
            elif accion == 'login':
                respuesta = iniciar_sesion(email, password)
                usuario = respuesta.get('data') if isinstance(respuesta, dict) else None
                if not isinstance(usuario, dict) or not usuario.get('id'):
                    raise BackendAPIError('La API no devolvió los datos de sesión.')
                session['usuario'] = {
                    'id': usuario['id'],
                    'nombre': usuario.get('nombre', ''),
                    'email': usuario.get('email', email),
                    'rol': usuario.get('rol', 'cliente'),
                }
                destino = _safe_next_url(request.args.get('next'))
                if destino:
                    return redirect(destino)
                if session.get('checkout'):
                    return redirect(url_for('web.site.compra.servicios'))
                flash('Iniciaste sesión correctamente.', 'success')
            else:
                flash('La acción solicitada no es válida.', 'error')
        except BackendAPIError as error:
            flash(str(error), 'error')

        if accion == 'login' and session.get('usuario'):
            if session.get('checkout'):
                return redirect(url_for('web.site.compra.servicios'))
            return redirect(url_for('web.site.home.index'))

    return render_template('site/login.html')


@login_bp.route('/logout', methods=['POST'])
def logout():
    session.pop('usuario', None)
    session.pop('checkout', None)
    session.pop('ultima_compra_id', None)
    flash('Cerraste sesión.', 'success')
    return redirect(url_for('web.site.home.index'))