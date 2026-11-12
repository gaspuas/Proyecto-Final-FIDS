import unittest
from unittest.mock import patch

from app import app


class AdminAccessTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def iniciar_sesion_como(self, rol):
        with self.client.session_transaction() as sesion:
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
        self.assertEqual(self.client.get('/api/admin/peliculas').status_code, 401)

        self.iniciar_sesion_como('cliente')
        self.assertEqual(self.client.get('/api/admin/peliculas').status_code, 403)

        self.iniciar_sesion_como('administrador')
        with patch(
            'backend.src.routes.admin.procesar_listar_todas_las_peliculas',
            return_value={'exito': True, 'datos': []},
        ):
            respuesta = self.client.get('/api/admin/peliculas')

        self.assertEqual(respuesta.status_code, 200)

    def test_login_admin_redirige_al_panel(self):
        with patch(
            'frontend.web.routes.site.login.iniciar_sesion',
            return_value={
                'data': {
                    'id': 1,
                    'nombre': 'Administradora',
                    'email': 'admin@example.test',
                    'rol': 'administrador',
                }
            },
        ):
            respuesta = self.client.post(
                '/login',
                data={
                    'accion': 'login',
                    'email': 'admin@example.test',
                    'password': 'password',
                },
            )

        self.assertEqual(respuesta.status_code, 302)
        self.assertEqual(respuesta.location, '/admin/')


if __name__ == '__main__':
    unittest.main()
