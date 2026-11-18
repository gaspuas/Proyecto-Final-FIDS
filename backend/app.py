"""Punto de entrada del backend: solo API REST. Ejecutar con `python -m backend.app`."""
import logging
import os
import secrets
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify

from backend.src.routes import register_api_routes

ROOT_DIR = Path(__file__).resolve().parent.parent

load_dotenv(ROOT_DIR / '.env')

app = Flask(__name__)
app.json.sort_keys = False

# La API admin lee la cookie de sesión firmada por el frontend, por eso
# ambos procesos DEBEN compartir el mismo SECRET_KEY (definirlo en .env).
if not os.getenv('SECRET_KEY'):
    logging.getLogger(__name__).warning(
        'SECRET_KEY no está definido: las sesiones de administrador no '
        'funcionarán entre el frontend y el backend.'
    )
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') or secrets.token_hex(32)

register_api_routes(app)


@app.get('/health')
def health():
    return jsonify({'status': 'success', 'message': 'Backend activo'}), 200


def _error(status, description):
    return jsonify({'status': 'error', 'errors': [{'description': description}]}), status


@app.errorhandler(404)
def not_found(error):
    return _error(404, error.description)


@app.errorhandler(500)
def internal_server_error(error):
    return _error(500, error.description)


if __name__ == '__main__':
    port = int(os.getenv('BACKEND_PORT', 5001))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() in ('true', '1', 't')
    print(f'Backend iniciado en http://localhost:{port}')
    app.run(host='0.0.0.0', port=port, debug=debug, threaded=True)
