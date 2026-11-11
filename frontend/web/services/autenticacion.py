from frontend.web.services.api_client import api_request


def iniciar_sesion(email, password):
    return api_request(
        'POST',
        '/api/auth/login',
        payload={'email': email, 'password': password},
    )


def registrar_usuario(nombre, email, password):
    return api_request(
        'POST',
        '/api/auth/register',
        payload={'nombre': nombre, 'email': email, 'password': password},
    )
