"""Punto de entrada del frontend: páginas Flask y sesiones del lado del servidor."""
from datetime import timedelta
import os
import secrets
from pathlib import Path

from cachelib import FileSystemCache
from dotenv import load_dotenv
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_session import Session

from frontend.web.routes import web_bp
from frontend.web.services.api_client import BackendAPIError
from frontend.web.utils.csrf import csrf_token_form

FRONTEND_DIR = Path(__file__).resolve().parent
ROOT_DIR = FRONTEND_DIR.parent
load_dotenv(ROOT_DIR / '.env')

app = Flask(
    __name__, template_folder=str(FRONTEND_DIR / 'templates'),
    static_folder=str(FRONTEND_DIR / 'static'),
)
app.json.sort_keys = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') or secrets.token_hex(32)
app.config.update(
    SESSION_TYPE='cachelib',
    SESSION_CACHELIB=FileSystemCache(cache_dir=str(ROOT_DIR / '.cine_session_cache'), threshold=1000),
    SESSION_PERMANENT=True,
    PERMANENT_SESSION_LIFETIME=timedelta(hours=2),
    SESSION_USE_SIGNER=True,
    SESSION_COOKIE_NAME='cine_paradiso_session',
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=os.getenv('SESSION_COOKIE_SECURE', 'false').lower() in ('true', '1'),
)
# IMPORTANTE: el access_token queda exclusivamente en la sesión del servidor,
# no dentro de una cookie Flask serializada y legible por el navegador.
Session(app)
app.register_blueprint(web_bp)


@app.context_processor
def inyectar_csrf():
    return {'csrf_token_global': csrf_token_form}


@app.get('/health')
def health():
    return jsonify({'status': 'success', 'message': 'Cine Paradiso activo'}), 200


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html', error_message=error.description), 404


@app.errorhandler(500)
def internal_server_error(error):
    return render_template('500.html', error_title='Ocurrió un error',
                           error_message='No pudimos completar la solicitud. Intenta más tarde.',
                           error_status_code=500), 500


@app.errorhandler(BackendAPIError)
def backend_unavailable(error):
    if error.status_code == 401:
        session.pop('usuario', None)
        session.pop('access_token', None)
        flash('Tu sesión expiró. Iniciá sesión nuevamente.', 'error')
        return redirect(url_for('web.site.login.index', next=request.path))
    return render_template('500.html', error_title='No se pudo completar la solicitud',
                           error_message=str(error), error_status_code=error.status_code), error.status_code


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() in ('true', '1', 't')
    print(f'Cine Paradiso iniciado en http://localhost:{port}')
    app.run(host='0.0.0.0', port=port, debug=debug, threaded=True)
