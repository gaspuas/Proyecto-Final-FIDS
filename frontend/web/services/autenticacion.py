"""Login y registro contra /api/auth."""
from frontend.web.services.api_client import BackendAPIError, api_request

CAMPOS_USUARIO = ('id', 'nombre', 'email', 'rol')


def iniciar_sesion(email, password):
    """Devuelve los datos minimos del usuario para la sesion web.

    El token que entrega la API no se guarda: hoy ningun endpoint lo valida.
    """
    try:
        payload = api_request(
            'POST',
            '/api/auth/login',
            payload={'email': email, 'password': password},
        )
    except BackendAPIError as error:
        if error.status_code == 401:
            raise BackendAPIError('El email o la contraseña no son correctos.', 401) from error
        raise

    usuario = payload.get('data') if isinstance(payload, dict) else None
    if not isinstance(usuario, dict) or not all(campo in usuario for campo in CAMPOS_USUARIO):
        raise BackendAPIError('El servidor devolvió una respuesta inválida al iniciar sesión.')
    return {campo: usuario[campo] for campo in CAMPOS_USUARIO}


def registrar_usuario(nombre, email, password):
    return api_request(
        'POST',
        '/api/auth/register',
        payload={'nombre': nombre, 'email': email, 'password': password},
    )
