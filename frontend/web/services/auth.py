"""Login y registro contra /api/auth."""
from frontend.web.services.api import ErrorApi, consultar_api

CAMPOS_USUARIO = ('id', 'nombre', 'email', 'rol')


def autenticar(email, password):
    """Devuelve los datos minimos del usuario para la sesion web.

    El token que entrega la API no se guarda: hoy ningun endpoint lo valida.
    """
    try:
        datos = consultar_api(
            'POST', '/api/auth/login',
            json={'email': email, 'password': password},
            mensaje_error='No pudimos iniciar sesión. Intentá de nuevo.',
        )
    except ErrorApi as error:
        if error.status == 401:
            raise ErrorApi('El email o la contraseña no son correctos.', 401) from error
        raise

    usuario = datos.get('data') if isinstance(datos, dict) else None
    if not isinstance(usuario, dict) or not all(campo in usuario for campo in CAMPOS_USUARIO):
        raise ErrorApi('El servidor devolvió una respuesta inválida al iniciar sesión.')
    return {campo: usuario[campo] for campo in CAMPOS_USUARIO}


def registrar(nombre, email, password):
    consultar_api(
        'POST', '/api/auth/register',
        json={'nombre': nombre, 'email': email, 'password': password},
        esperados=(201,),
        mensaje_error='No pudimos crear la cuenta. Intentá de nuevo.',
    )
