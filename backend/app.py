from flask import Flask
from backend.src.routes.auth import auth_bp
from backend.src.routes.compras import compras_bp
from backend.src.routes.funciones import funciones_bp

from backend.src.routes.peliculas import peliculas_bp
from backend.src.routes.servicios import servicios_bp
app = Flask(__name__)

app.register_blueprint(auth_bp)
app.register_blueprint(compras_bp)
app.register_blueprint(funciones_bp)
app.register_blueprint(peliculas_bp)
app.register_blueprint(servicios_bp)

@app.route('/')
def home():
    return "Backend Cine Paradiso activo"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
