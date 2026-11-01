def validar_registro(data):
    if not data:
        return False, "El cuerpo de la petición debe ser JSON."
    
    if not data.get('nombre') or not str(data.get('nombre')).strip():
        return False, "El campo 'nombre' es obligatorio."
        
    if not data.get('email') or not str(data.get('email')).strip():
        return False, "El campo 'email' es obligatorio."
        
    if not data.get('password') or len(str(data.get('password'))) < 6:
        return False, "El campo 'password' es obligatorio y debe tener al menos 6 caracteres."
        
    return True, None

def validar_login(data):
    if not data or 'email' not in data or 'password' not in data:
        return False, "Faltan datos requeridos: 'email' y 'password'."
    
    if not isinstance(data['email'], str) or not isinstance(data['password'], str):
        return False, "Tipos de datos inválidos para las credenciales."
        
    return True, None