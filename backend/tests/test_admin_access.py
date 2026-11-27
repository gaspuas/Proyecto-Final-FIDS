import unittest
from unittest.mock import patch

from backend.app import app as backend_app
from frontend.app import app as frontend_app


class AdminAccessTests(unittest.TestCase):
    def setUp(self):
        self.client = frontend_app.test_client()
        self.api_client = backend_app.test_client()

    def iniciar_sesion_como(self, rol, client=None):
        with (client or self.client).session_transaction() as sesion:
            sesion['usuario'] = {
                'id': 1,
                'nombre': 'Usuario de prueba',
                'email': 'usuario@example.test',
                'rol': rol,
            }

    def test_usuario_sin_sesion_es_enviado_al_login(self):
        respuesta = self.client.get('/admin/peliculas/')

        self.assertEqual(respuesta.status_code, 302)
        self.assertEqual(respuesta.location, '/login?next=/admin/peliculas/')

    def test_cliente_no_puede_abrir_pantallas_admin(self):
        self.iniciar_sesion_como('cliente')

        respuesta = self.client.get('/admin/peliculas/')

        self.assertEqual(respuesta.status_code, 403)

    def test_administrador_puede_abrir_panel(self):
        self.iniciar_sesion_como('administrador')
        with patch(
            'frontend.web.routes.admin.peliculas.obtener_todas_las_peliculas',
            return_value=[],
        ):
            respuesta = self.client.get('/admin/peliculas/')

        self.assertEqual(respuesta.status_code, 200)
        self.assertIn(b'Administraci', respuesta.data)

    def test_api_admin_requiere_rol_administrador(self):
        api = self.api_client
        self.assertEqual(api.get('/api/admin/peliculas').status_code, 401)

        token = 'a' * 43
        headers = {'Authorization': f'Bearer {token}'}
        with patch('backend.src.utils.token_auth.buscar_usuario_por_token',
                   return_value={'id': 1, 'rol': 'cliente', 'nombre': 'Cliente', 'email': 'c@test.test'}):
            self.assertEqual(api.get('/api/admin/peliculas', headers=headers).status_code, 403)

        with patch('backend.src.utils.token_auth.buscar_usuario_por_token',
                   return_value={'id': 1, 'rol': 'administrador', 'nombre': 'Admin', 'email': 'a@test.test'}), patch(
            'backend.src.routes.admin.procesar_listar_todas_las_peliculas',
            return_value={'exito': True, 'datos': []},
        ):
            respuesta = api.get('/api/admin/peliculas', headers=headers)

        self.assertEqual(respuesta.status_code, 200)

    def test_login_admin_redirige_al_panel(self):
        with self.client.session_transaction() as sesion:
            sesion['csrf_token_global'] = 'testcsrf'
        with patch(
            'frontend.web.routes.site.login.iniciar_sesion',
            return_value={
                'data': {
                    'id': 1,
                    'nombre': 'Administradora',
                    'email': 'admin@example.test',
                    'rol': 'administrador',
                    'token': 'a' * 43,
                }
            },
        ):
            respuesta = self.client.post(
                '/login',
                data={
                    'csrf_token': 'testcsrf',
                    'accion': 'login',
                    'email': 'admin@example.test',
                    'password': 'password',
                },
            )

        self.assertEqual(respuesta.status_code, 302)
        self.assertEqual(respuesta.location, '/admin/')


if __name__ == '__main__':
    unittest.main()
