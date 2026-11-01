from backend.src.repositories.auth_repository import *
from backend.src.validators.auth_validators import *
from werkzeug.security import generate_password_hash, check_password_hash
from secrets import token_urlsafe 
import datetime
from flask import current_app

def registrar_cliente_servicio(data):
    nombre = data.get('nombre')
    email = data.get('email')
    password = data.get('password')

    password_hash = generate_password_hash(password)

    return crear_usuario_cliente(nombre, email, password_hash)

def procesar_login(data):
    es_valido, mensaje_error = validar_login(data)
    if not es_valido:
        return {'exito': False, 'mensaje': mensaje_error, 'tipo_error': 'VALIDATION'}

    usuario = obtener_usuario_por_email(data['email'])
    if not usuario:
        return {'exito': False, 'mensaje': 'Credenciales inválidas.', 'tipo_error': 'UNAUTHORIZED'}

    if not check_password_hash(usuario['password_hash'], data['password']):
        return {'exito': False, 'mensaje': 'Credenciales inválidas.', 'tipo_error': 'UNAUTHORIZED'}

    token = token_urlsafe(32)
    
    fecha_expiracion = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=2)

    datos_usuario = {
        'id': usuario['id'],
        'nombre': usuario['nombre'],
        'email': usuario['email'],
        'rol': usuario['rol'],
        'token': token,
        'expira_en': fecha_expiracion.isoformat() 
    }

    return {'exito': True, 'mensaje': 'Autenticación exitosa.', 'datos': datos_usuario}