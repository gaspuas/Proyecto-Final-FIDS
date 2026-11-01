from flask import Flask
from backend.src.routes.auth import auth_bp

app = Flask(__name__)

app.register_blueprint(auth_bp)

@app.route('/')
def home():
    return "Backend Cine Paradiso activo"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)