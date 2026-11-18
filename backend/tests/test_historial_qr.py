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
        'entradas': [
            {
                'pelicula_titulo': 'Prueba',
                'fecha_hora': '2026-12-01 20:00:00',
                'numero_butaca': butaca,
                'precio': '100.00',
                'nombre_local': 'Paradiso Central',
                'numero_sala': 1,
            }
            for butaca in ('C7', 'C8')
        ],
        'servicios': [
            {'id': 1, 'nombre': 'Combo', 'cant': 2, 'subtotal': '9000.00'},
        ],
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

    def test_la_tarjeta_del_historial_tiene_el_mismo_detalle_que_la_confirmacion(self):
        compra = _compra(1, 'activo')
        compra['qr_data_uri'] = QR_FALSO
        compra['monto_total'] = '9200.00'

        html = self._historial([compra])

        self.assertIn('class="compra__tarjeta confirmacion"', html)
        self.assertIn('Prueba · 2026-12-01 20:00:00 · Butacas C7, C8', html)
        self.assertIn('Entradas (2)', html)
        self.assertIn('$200.00', html)
        self.assertIn('Combo × 2', html)
        self.assertIn('$9000.00', html)
        self.assertIn('$9200.00', html)
        self.assertIn('Cancelar compra', html)

    def test_una_compra_cancelada_se_ve_como_cancelada_y_sin_boton_de_cancelar(self):
        html = self._historial([_compra(2, 'cancelado')])

        self.assertIn('confirmacion--cancelada', html)
        self.assertIn('Compra cancelada', html)
        self.assertNotIn('Cancelar compra', html)


class ConfirmacionVistaTests(unittest.TestCase):
    def test_la_confirmacion_usa_la_misma_tarjeta_que_el_historial(self):
        client = frontend_app.test_client()
        with client.session_transaction() as sesion:
            sesion['usuario'] = {'id': 1, 'nombre': 'Cliente', 'rol': 'cliente'}
            sesion['checkout'] = {'id_funcion': 1, 'butacas': ['A1', 'A2']}

        with patch(
            'frontend.web.routes.site.compra.obtener_funcion',
            return_value={
                'id': 1,
                'precio_base': 100,
                'pelicula_titulo': 'Prueba',
                'fecha_hora': '2026-12-01 20:00:00',
            },
        ), patch(
            'frontend.web.routes.site.compra.obtener_servicios', return_value=[]
        ), patch(
            'frontend.web.routes.site.compra.crear_compra',
            return_value={
                'id': 7,
                'codigo_qr': 'codigo-7',
                'qr_data_uri': QR_FALSO,
                'monto_total': 200,
            },
        ):
            html = client.post('/compra/servicios').get_data(as_text=True)

        self.assertIn('class="compra__tarjeta confirmacion"', html)
        self.assertIn('Compra confirmada', html)
        self.assertIn('Prueba · 2026-12-01 20:00:00 · Butacas A1, A2', html)
        self.assertIn(f'src="{QR_FALSO}"', html)
        self.assertIn('Cancelar compra', html)
        self.assertIn('Volver al inicio', html)


if __name__ == '__main__':
    unittest.main()
