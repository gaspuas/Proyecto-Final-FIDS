from urllib.parse import urlparse

from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for

from frontend.web.services.api_client import BackendAPIError
from frontend.web.services.autenticacion import iniciar_sesion, registrar_usuario, cerrar_sesion_backend
from frontend.web.utils.csrf import requerir_csrf

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
        requerir_csrf()
        accion = request.form.get('accion')
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        try:
            if accion == 'registro':
                registrar_usuario(
                    request.form.get('nombre', '').strip(),
                    email,
                    password,
                    request.form.get('password_confirmacion', ''),
                    request.form.get('fecha_nacimiento', ''),
                    request.form.get('acepta_terminos') == '1',
                    request.form.get('recibir_promociones') == '1',
                )
                flash('Tu cuenta fue creada. Ya podés iniciar sesión.', 'success')
            elif accion == 'login':
                respuesta = iniciar_sesion(email, password)
                usuario = respuesta.get('data') if isinstance(respuesta, dict) else None
                if (not isinstance(usuario, dict) or not usuario.get('id')
                        or not isinstance(usuario.get('token'), str) or not usuario.get('token')):
                    raise BackendAPIError('La API no devolvió un TokenSession válido.')
                # Renueva sesión para prevenir fijación, conservando solo un checkout pendiente.
                checkout_pendiente = session.get('checkout')
                session.clear()
                session['access_token'] = usuario['token']
                # Rotar con contenido: Flask-Session regenera solamente sesiones no vacías.
                current_app.session_interface.regenerate(session)
                session.permanent = True
                if checkout_pendiente:
                    session['checkout'] = checkout_pendiente
                session['usuario'] = {
                    'id': usuario['id'],
                    'nombre': usuario.get('nombre', ''),
                    'email': usuario.get('email', email),
                    'rol': usuario.get('rol', 'cliente'),
                }
                destino = _safe_next_url(request.args.get('next'))
                if destino:
                    return redirect(destino)
                if session['usuario']['rol'] == 'administrador':
                    flash('Iniciaste sesión correctamente.', 'success')
                    return redirect(url_for('web.admin.index'))
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
    requerir_csrf()
    if session.get('access_token'):
        try:
            cerrar_sesion_backend()
        except BackendAPIError:
            # Cerramos la sesión web igualmente; si MySQL está caído, el token
            # del backend vencerá a las dos horas. No se informa revocación exitosa.
            session.clear()
            flash('Se cerró la sesión local. No se pudo confirmar la revocación en el backend.', 'error')
            return redirect(url_for('web.site.home.index'))
    session.clear()
    flash('Cerraste sesión.', 'success')
    return redirect(url_for('web.site.home.index'))