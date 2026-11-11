"""Sesion web: usuario autenticado, acceso por rol y proteccion CSRF de formularios.

Esta proteccion es solo de la capa web. No reemplaza la autorizacion que
debe hacer la API.
"""
import secrets
from functools import wraps
from urllib.parse import urlparse

from flask import redirect, render_template, request, session, url_for

ROL_ADMIN = 'administrador'

# La reserva en curso sobrevive al login para poder continuar la compra
CLAVES_QUE_SOBREVIVEN_AL_LOGIN = ('checkout',)


def usuario_actual():
    return session.get('usuario')


def es_admin(usuario):
    return bool(usuario) and usuario.get('rol') == ROL_ADMIN


def iniciar_sesion(usuario):
    conservadas = {
        clave: session[clave]
        for clave in CLAVES_QUE_SOBREVIVEN_AL_LOGIN
        if clave in session
    }
    session.clear()
    session.update(conservadas)
    session['usuario'] = usuario


def cerrar_sesion():
    session.clear()


def destino_seguro(url, por_defecto):
    """Acepta solo rutas internas para evitar redirecciones a otros sitios."""
    if url and url.startswith('/') and not url.startswith('//') and '\\' not in url:
        partes = urlparse(url)
        if not partes.scheme and not partes.netloc:
            return url
    return por_defecto


def _pagina_error(titulo, mensaje, status):
    return render_template('500.html', error_title=titulo, error_message=mensaje), status


def _redirigir_a_login():
    siguiente = request.full_path.rstrip('?') if request.method == 'GET' else None
    return redirect(url_for('web.site.login.index', next=siguiente))


def login_requerido(vista):
    @wraps(vista)
    def envoltura(*args, **kwargs):
        if usuario_actual() is None:
            return _redirigir_a_login()
        return vista(*args, **kwargs)
    return envoltura


def verificar_admin():
    """Para before_request: deja pasar solo a administradores."""
    usuario = usuario_actual()
    if usuario is None:
        return _redirigir_a_login()
    if not es_admin(usuario):
        return _pagina_error(
            '403 · Acceso denegado',
            'Esta sección es solo para administradores.',
            403,
        )
    return None


def token_csrf():
    if '_csrf' not in session:
        session['_csrf'] = secrets.token_urlsafe(32)
    return session['_csrf']


def csrf_requerido(vista):
    @wraps(vista)
    def envoltura(*args, **kwargs):
        esperado = session.get('_csrf')
        recibido = request.form.get('csrf_token', '')
        if not esperado or not secrets.compare_digest(recibido, esperado):
            return _pagina_error(
                '400 · Formulario vencido',
                'El formulario expiró. Volvé atrás, recargá la página e intentá de nuevo.',
                400,
            )
        return vista(*args, **kwargs)
    return envoltura
