import re
from datetime import date

def validar_registro(data):
    if not data:
        return False, "El cuerpo de la petición debe ser JSON."
    
    if not data.get('nombre') or not str(data.get('nombre')).strip():
        return False, "El campo 'nombre' es obligatorio."
        
    if not data.get('email') or not str(data.get('email')).strip():
        return False, "El campo 'email' es obligatorio."
        
    if not data.get('password') or len(str(data.get('password'))) < 6:
        return False, "El campo 'password' es obligatorio y debe tener al menos 6 caracteres."
        
    email = data.get('email')
    if not isinstance(email, str) or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email.strip()):
        return False, "Ingresá un email válido (nombre@dominio.com)."

    if data.get('password_confirmacion') != data.get('password'):
        return False, "Las contraseñas no coinciden."

    fecha_texto = data.get('fecha_nacimiento')
    if not isinstance(fecha_texto, str):
        return False, "La fecha de nacimiento es obligatoria."
    try:
        fecha = date.fromisoformat(fecha_texto)
    except ValueError:
        return False, "Ingresá una fecha de nacimiento válida."
    if fecha > date.today():
        return False, "La fecha de nacimiento no puede ser futura."

    if data.get('acepta_terminos') is not True:
        return False, "Debés aceptar los términos y condiciones para registrarte."
    if not isinstance(data.get('recibir_promociones', False), bool):
        return False, "La preferencia de promociones debe ser verdadera o falsa."

    return True, None

def validar_login(data):
    if not data or 'email' not in data or 'password' not in data:
        return False, "Faltan datos requeridos: 'email' y 'password'."
    
    if not isinstance(data['email'], str) or not isinstance(data['password'], str):
        return False, "Tipos de datos inválidos para las credenciales."
        
    return True, None