import unittest
from unittest.mock import patch

from backend.app import app as backend_app
from frontend.app import app as frontend_app

QR_FALSO = 'data:image/png;base64,AAAA'


def _compra(id_compra, estado):
    return {
        'id': id_compra,
        'usuario_id': 1,
        'fecha_compra': '2026-11-18 16:00:00',
        'monto_total': 200,
        'codigo_qr': f'codigo-{id_compra}',
        'estado_qr': estado,
        'entradas': [{
            'pelicula_titulo': 'Prueba',
            'fecha_hora': '2026-12-01 20:00:00',
            'numero_butaca': 'C7',
            'nombre_local': 'Paradiso Central',
            'numero_sala': 1,
        }],
        'servicios': [],
    }


class HistorialApiTests(unittest.TestCase):
    def _listar(self, compras):
        with patch(
            'backend.src.routes.compras.listar_compras_usuario_service',
            return_value=(compras, None, 200),
        ):
            return backend_app.test_client().get('/api/compras/usuario/1').get_json()

    def test_las_compras_activas_incluyen_la_imagen_del_qr(self):
        datos = self._listar([_compra(1, 'activo')])

        qr = datos['compras'][0]['qr_data_uri']
        self.assertTrue(qr.startswith('data:image/png;base64,'))

    def test_las_compras_canceladas_o_usadas_no_incluyen_qr(self):
        datos = self._listar([_compra(2, 'cancelado'), _compra(3, 'usado')])

        for compra in datos['compras']:
            self.assertNotIn('qr_data_uri', compra)


class HistorialVistaTests(unittest.TestCase):
    def _historial(self, compras):
        client = frontend_app.test_client()
        with client.session_transaction() as sesion:
            sesion['usuario'] = {'id': 1, 'nombre': 'Cliente', 'rol': 'cliente'}
        with patch(
            'frontend.web.routes.site.compra.obtener_compras_usuario',
            return_value=compras,
        ):
            return client.get('/compra/historial').get_data(as_text=True)

    def test_muestra_el_qr_de_la_compra_activa(self):
        compra = _compra(1, 'activo')
        compra['qr_data_uri'] = QR_FALSO

        html = self._historial([compra])

        self.assertIn(f'src="{QR_FALSO}"', html)
        self.assertIn('codigo-1', html)

    def test_no_muestra_qr_si_la_compra_no_esta_activa(self):
        html = self._historial([_compra(2, 'cancelado')])

        self.assertNotIn('data:image/png', html)


if __name__ == '__main__':
    unittest.main()
