import unittest
from unittest.mock import patch

from frontend.app import app

FUNCION = {
    'id': 1,
    'pelicula_titulo': 'Prueba',
    'fecha_hora': '2026-12-01 20:00:00',
    'nombre_local': 'Paradiso Central',
    'numero_sala': 1,
    'precio_base': 100,
    'capacidad_total': 6,
}


def _mapa():
    codigos = ['A1', 'A2', 'A3', 'B1', 'B2', 'B3']
    return {
        'columnas': 3,
        'butacas': [
            {
                'codigo': codigo,
                'fila': codigo[0],
                'columna': int(codigo[1:]),
                'libre': codigo != 'A2',
            }
            for codigo in codigos
        ],
    }


class ReservaButacasTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        patcher_mapa = patch(
            'frontend.web.routes.site.reserva.obtener_butacas', return_value=_mapa()
        )
        patcher_funcion = patch(
            'frontend.web.routes.site.reserva.obtener_funcion', return_value=FUNCION
        )
        patcher_mapa.start()
        patcher_funcion.start()
        self.addCleanup(patcher_mapa.stop)
        self.addCleanup(patcher_funcion.stop)

    def test_el_mapa_se_muestra_por_filas_con_letras_y_columnas_con_numeros(self):
        html = self.client.get('/reserva/1').get_data(as_text=True)

        self.assertIn('value="A1"', html)
        self.assertIn('value="B3"', html)
        self.assertIn('aria-label="Fila A, butaca 1"', html)
        self.assertEqual(html.count('class="mapa-cine__fila"'), 3)  # cabecera + 2 filas

    def test_acepta_codigos_de_butaca_libres(self):
        respuesta = self.client.post(
            '/reserva/butacas', data={'funcion_id': '1', 'asientos': ['A1', 'B3']}
        )

        self.assertEqual(respuesta.status_code, 302)
        with self.client.session_transaction() as sesion:
            self.assertEqual(sesion['checkout']['butacas'], ['A1', 'B3'])

    def test_rechaza_numeros_sueltos(self):
        respuesta = self.client.post(
            '/reserva/butacas', data={'funcion_id': '1', 'asientos': ['13']}
        )

        self.assertEqual(respuesta.status_code, 400)

    def test_avisa_si_la_butaca_ya_esta_ocupada(self):
        respuesta = self.client.post(
            '/reserva/butacas', data={'funcion_id': '1', 'asientos': ['A2']}
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertIn('ya no están disponibles'.encode(), respuesta.data)


if __name__ == '__main__':
    unittest.main()
