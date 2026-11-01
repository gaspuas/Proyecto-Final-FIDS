from flask import Flask
from backend.src.routes.auth import auth_bp
from backend.src.routes.compras import compras_bp
app = Flask(__name__)

app.register_blueprint(auth_bp)
app.register_blueprint(compras_bp)


@app.route('/')
def home():
    return "Backend Cine Paradiso activo"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
