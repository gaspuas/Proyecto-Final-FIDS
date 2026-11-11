import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template

from backend.src.routes import register_api_routes
from frontend.web.routes import web_bp
from frontend.web.services.api_client import BackendAPIError

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / 'frontend'

load_dotenv(BASE_DIR / '.env')

app = Flask(
    __name__,
    template_folder=str(FRONTEND_DIR / 'templates'),
    static_folder=str(FRONTEND_DIR / 'static'),
)
app.json.sort_keys = False
app.config['SECRET_KEY'] = os.getenv(
    'SECRET_KEY', 'cine_paradiso_secret_key_2026'
)

register_api_routes(app)
app.register_blueprint(web_bp)


@app.get('/health')
def health():
    return jsonify({'status': 'success', 'message': 'Cine Paradiso activo'}), 200


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html', error_message=error.description), 404


@app.errorhandler(500)
def internal_server_error(error):
    return render_template('500.html', error_message=error.description), 500


@app.errorhandler(BackendAPIError)
def backend_unavailable(error):
    return render_template(
        '500.html',
        error_title='503 · Backend no disponible',
        error_message=str(error),
    ), error.status_code if 400 <= error.status_code < 500 else 503


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() in ('true', '1', 't')
    print(f'Cine Paradiso iniciado en http://localhost:{port}')
    app.run(host='0.0.0.0', port=port, debug=debug, threaded=True)
