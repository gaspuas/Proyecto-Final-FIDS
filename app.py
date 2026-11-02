import os
from flask import Flask, render_template
from dotenv import load_dotenv
from backend.src.routes import web_bp
from backend.src.routes.auth import auth_bp
from backend.src.routes.compras import compras_bp
from backend.src.routes.funciones import funciones_bp
from backend.src.routes.peliculas import peliculas_bp

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
)

app.json.sort_keys = False
app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY", "cine_paradiso_secret_key_2026"
)

app.register_blueprint(web_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(compras_bp)
app.register_blueprint(funciones_bp)
app.register_blueprint(peliculas_bp)


@app.errorhandler(404)
def page_not_found(e):
    if os.path.exists(os.path.join(BASE_DIR, "templates", "404.html")):
        return render_template("404.html"), 404
    return "Página no encontrada", 404


@app.errorhandler(500)
def internal_server_error(e):
    if os.path.exists(os.path.join(BASE_DIR, "templates", "500.html")):
        return render_template("500.html"), 500
    return "Error interno del servidor", 500


if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "True").lower() in ["true", "1", "t"]

    print(f"Servidor Cine Paradiso iniciado en http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=debug)