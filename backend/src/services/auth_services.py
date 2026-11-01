from backend.src.repositories.auth_repository import *
from werkzeug.security import generate_password_hash

def registrar_cliente_service(data):
    nombre = data.get('nombre')
    email = data.get('email')
    password = data.get('password')

    # Hashear la contraseña por seguridad
    password_hash = generate_password_hash(password)

    # Llamar al repositorio para guardar en base de datos
    return crear_usuario_cliente(nombre, email, password_hash)