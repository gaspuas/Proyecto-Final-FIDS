import unittest
from unittest.mock import Mock, patch

import requests

from app import app


class BackendAPIErrorTests(unittest.TestCase):
    def test_api_internal_error_keeps_500_status_and_detail(self):
        response_backend = Mock(
            status_code=500,
            content=b'{"errors":[{"description":"Database transaction failed"}]}',
            ok=False,
        )
        response_backend.json.return_value = {
            'errors': [{'description': 'Database transaction failed'}]
        }

        with patch(
            'frontend.web.services.api_client.requests.request',
            return_value=response_backend,
        ):
            response = app.test_client().get('/peliculas/')

        self.assertEqual(response.status_code, 500)
        self.assertIn(b'500', response.data)
        self.assertIn(b'Database transaction failed', response.data)

    def test_purchase_timeout_warns_that_result_may_be_uncertain(self):
        client = app.test_client()
        with client.session_transaction() as state:
            state['usuario'] = {'id': 2, 'nombre': 'Cliente', 'rol': 'cliente'}
            state['checkout'] = {'id_funcion': 1, 'butacas': ['1']}

        with patch(
            'frontend.web.routes.site.compra.obtener_funcion',
            return_value={'id': 1, 'precio_base': 100, 'pelicula_titulo': 'Test'},
        ), patch(
            'frontend.web.routes.site.compra.obtener_servicios',
            return_value=[],
        ), patch(
            'frontend.web.services.api_client.requests.request',
            side_effect=requests.Timeout,
        ):
            response = client.post('/compra/servicios')

        self.assertEqual(response.status_code, 504)
        self.assertIn('podría haberse registrado'.encode(), response.data)
        self.assertIn(b'historial', response.data)


if __name__ == '__main__':
    unittest.main()
