"""Security regressions for TokenSession and object-level authorization."""
import unittest
from unittest.mock import patch

from backend.app import app as backend_app
from frontend.app import app as frontend_app

TOKEN = 'a' * 43
HEADERS = {'Authorization': 'Bearer ' + TOKEN}
CLIENTE = {'id': 2, 'nombre': 'Cliente', 'email': 'cliente@test.test', 'rol': 'cliente'}
ADMIN = {'id': 7, 'nombre': 'Admin', 'email': 'admin@test.test', 'rol': 'administrador'}


class AutorizacionAPITests(unittest.TestCase):
    def setUp(self):
        self.client = backend_app.test_client()

    def test_endpoints_protegidos_rechazan_sin_bearer(self):
        self.assertEqual(self.client.get('/api/auth/me').status_code, 401)
        self.assertEqual(self.client.get('/api/compras/mis').status_code, 401)
        self.assertEqual(self.client.post('/api/compras', json={}).status_code, 401)
        self.assertEqual(self.client.patch('/api/compras/1/cancelar').status_code, 401)
        self.assertEqual(self.client.get('/api/admin/peliculas').status_code, 401)
        self.assertEqual(self.client.get('/api/novedades/admin/todas').status_code, 401)

    def test_token_invalido_o_revocado_rechazado(self):
        with patch('backend.src.utils.token_auth.buscar_usuario_por_token', return_value=None):
            self.assertEqual(self.client.get('/api/auth/me', headers=HEADERS).status_code, 401)

    def test_me_retorna_identidad_validada(self):
        with patch('backend.src.utils.token_auth.buscar_usuario_por_token', return_value=CLIENTE):
            response = self.client.get('/api/auth/me', headers=HEADERS)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['data']['id'], 2)

    def test_cliente_no_puede_operar_novedades_admin(self):
        with patch('backend.src.utils.token_auth.buscar_usuario_por_token', return_value=CLIENTE):
            response = self.client.get('/api/novedades/admin/todas', headers=HEADERS)
        self.assertEqual(response.status_code, 403)

    def test_crear_compra_usa_id_validado_no_id_enviado(self):
        body = {'id_funcion': 3, 'butacas': ['A1'], 'servicios': []}
        with patch('backend.src.utils.token_auth.buscar_usuario_por_token', return_value=CLIENTE), patch(
            'backend.src.routes.compras.crear_compra_service',
            return_value=({'id': 10, 'codigo_qr': 'codigo_prueba'}, None, 201)
        ) as crear, patch('backend.src.routes.compras.generar_qr_base64', return_value='data:image/png;base64,TEST'):
            resp = self.client.post('/api/compras', json=body, headers=HEADERS)
        self.assertEqual(resp.status_code, 201)
        crear.assert_called_once_with(id_usuario=2, id_funcion=3, butacas=['A1'], servicios=[])

    def test_cliente_no_puede_elegir_id_usuario_ajeno(self):
        with patch('backend.src.utils.token_auth.buscar_usuario_por_token', return_value=CLIENTE):
            response = self.client.post('/api/compras', json={
                'id_usuario': 999, 'id_funcion': 3, 'butacas': ['A1']
            }, headers=HEADERS)
        self.assertEqual(response.status_code, 400)

    def test_historial_de_otra_persona_es_404(self):
        with patch('backend.src.utils.token_auth.buscar_usuario_por_token', return_value=CLIENTE), patch(
            'backend.src.routes.compras.listar_compras_usuario_service'
        ) as listar:
            response = self.client.get('/api/compras/usuario/999', headers=HEADERS)
        self.assertEqual(response.status_code, 404)
        listar.assert_not_called()

    def test_cancelacion_se_vincula_al_usuario_de_token(self):
        with patch('backend.src.utils.token_auth.buscar_usuario_por_token', return_value=CLIENTE), patch(
            'backend.src.routes.compras.cancelar_compra_service',
            return_value=({'id': 5, 'estado_qr': 'cancelado'}, None, 200)
        ) as cancelar:
            response = self.client.patch('/api/compras/5/cancelar', headers=HEADERS)
        self.assertEqual(response.status_code, 200)
        cancelar.assert_called_once_with(5, 2)

    def test_logout_revoca_hash_del_token(self):
        with patch('backend.src.utils.token_auth.buscar_usuario_por_token', return_value=CLIENTE), patch(
            'backend.src.routes.auth.revocar_sesion'
        ) as revocar:
            response = self.client.post('/api/auth/logout', headers=HEADERS)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(revocar.call_args.args[0]), 64)


class SeguridadFrontendTests(unittest.TestCase):
    def test_logout_rechaza_formulario_sin_csrf(self):
        client = frontend_app.test_client()
        with client.session_transaction() as estado:
            estado['usuario'] = CLIENTE
        self.assertEqual(client.post('/logout').status_code, 400)

    def test_token_no_se_envia_en_cookie_flask_comun(self):
        # Las cookies contienen un ID opaco para buscar una sesión del servidor.
        self.assertEqual(frontend_app.config['SESSION_TYPE'], 'cachelib')
        self.assertTrue(frontend_app.config['SESSION_COOKIE_HTTPONLY'])
        self.assertEqual(frontend_app.config['SESSION_COOKIE_SAMESITE'], 'Lax')


if __name__ == '__main__':
    unittest.main()

class PropiedadCompraTests(unittest.TestCase):
    def test_servicio_rechaza_cancelar_compra_de_tercero(self):
        from backend.src.services.compras_services import cancelar_compra_service
        with patch('backend.src.services.compras_services.obtener_compra_por_id_db',
                   return_value={'id': 5, 'usuario_id': 99, 'estado_qr': 'activo'}), patch(
            'backend.src.services.compras_services.obtener_fecha_funcion_compra_db'
        ) as fecha:
            compra, mensaje, estado = cancelar_compra_service(5, 2)
        self.assertIsNone(compra)
        self.assertEqual(estado, 404)
        fecha.assert_not_called()
