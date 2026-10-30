import os
from flask import Flask, render_template
from dotenv import load_dotenv
from web.routes import web_bp

# Cargar variables de entorno desde el archivo .env
load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__,
            template_folder=os.path.join(BASE_DIR, 'templates'),
            static_folder=os.path.join(BASE_DIR, 'static'))

app.json.sort_keys = False

    # Configuración de sesión y claves secretas
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'cine_paradiso_secret_key_2026')

    # -----------------------------------------------------------------
    # Registro de Blueprints (Rutas Web)
    # -----------------------------------------------------------------
app.register_blueprint(web_bp)
    # -----------------------------------------------------------------
    # Manejo de Errores HTTP
    # -----------------------------------------------------------------
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404 if os.path.exists('templates/404.html') else ("Página no encontrada", 404)

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500 if os.path.exists('templates/500.html') else ("Página no encontrada", 500)


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() in ['true', '1', 't']
    
    print(f"🎬 Servidor Cine Paradiso iniciado en http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=debug)