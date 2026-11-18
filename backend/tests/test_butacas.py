import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

from backend.src.services import compras_services, funciones_services
from backend.src.utils.butacas import es_codigo_valido, generar_codigos
from backend.src.validators.compras_validators import validar_body_crear_compra


class CodigosDeButacaTests(unittest.TestCase):
    def test_genera_codigos_por_fila_y_columna(self):
        self.assertEqual(
            generar_codigos(2, 3),
            ['A1', 'A2', 'A3', 'B1', 'B2', 'B3'],
        )

    def test_codigo_valido_dentro_de_la_sala(self):
        self.assertTrue(es_codigo_valido('A1', 5, 10))
        self.assertTrue(es_codigo_valido('E10', 5, 10))

    def test_codigo_invalido_fuera_de_la_sala_o_con_formato_incorrecto(self):
        for codigo in ('F1', 'A11', 'A0', '13', 'a1', 'AA1', '', 'A', None):
            with self.subTest(codigo=codigo):
                self.assertFalse(es_codigo_valido(codigo, 5, 10))


class MapaDeButacasTests(unittest.TestCase):
    def test_el_mapa_usa_codigos_y_marca_filas_y_columnas(self):
        funcion = {'capacidad_total': 6, 'filas': 2, 'columnas': 3}
        with patch.object(
            funciones_services, 'obtener_funcion_por_id_db', return_value=funcion
        ), patch.object(
            funciones_services, 'obtener_butacas_ocupadas_db', return_value={'A2'}
        ):
            mapa, error, status = funciones_services.consultar_butacas_funcion_service(1)

        self.assertIsNone(error)
        self.assertEqual(status, 200)
        self.assertEqual(
            [b['codigo'] for b in mapa['butacas']],
            ['A1', 'A2', 'A3', 'B1', 'B2', 'B3'],
        )
        a2 = mapa['butacas'][1]
        self.assertEqual((a2['fila'], a2['columna']), ('A', 2))
        self.assertFalse(a2['libre'])
        self.assertEqual(mapa['ocupadas'], ['A2'])
        self.assertEqual(mapa['libres'], ['A1', 'A3', 'B1', 'B2', 'B3'])


class ValidadorDeCompraTests(unittest.TestCase):
    def _body(self, butacas):
        return {'id_usuario': 1, 'id_funcion': 1, 'butacas': butacas}

    def test_acepta_codigos_y_los_normaliza_a_mayusculas(self):
        datos, error = validar_body_crear_compra(self._body(['a1', 'B10']))

        self.assertIsNone(error)
        self.assertEqual(datos['butacas'], ['A1', 'B10'])

    def test_rechaza_numeros_sueltos(self):
        _, error = validar_body_crear_compra(self._body(['13']))

        self.assertIsNotNone(error)


class CompraConButacasTests(unittest.TestCase):
    def _crear(self, butacas):
        funcion = {
            'id': 1,
            'sala_id': 1,
            'fecha_hora': datetime.now() + timedelta(days=1),
            'precio_base': 100,
            'capacidad_total': 50,
            'filas': 5,
            'columnas': 10,
        }
        with patch.object(
            compras_services, 'obtener_usuario_por_id_db', return_value={'id': 1}
        ), patch.object(
            compras_services, 'obtener_funcion_por_id_db', return_value=funcion
        ), patch.object(
            compras_services, 'obtener_butacas_ocupadas_db', return_value=set()
        ):
            return compras_services.crear_compra_service(1, 1, butacas, [])

    def test_rechaza_butaca_fuera_de_la_sala(self):
        compra, error, status = self._crear(['F1'])

        self.assertIsNone(compra)
        self.assertEqual(status, 400)
        self.assertIn('F1', error)

    def test_rechaza_numero_suelto_aunque_este_dentro_de_la_capacidad(self):
        compra, error, status = self._crear(['13'])

        self.assertIsNone(compra)
        self.assertEqual(status, 400)


if __name__ == '__main__':
    unittest.main()
