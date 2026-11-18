import unittest
from pathlib import Path
from unittest.mock import patch

from backend.src.repositories import compras_repository

SCHEMA = Path(__file__).resolve().parents[2] / 'database' / 'schema.sql'


class CursorFalso:
    def __init__(self, eventos, estado_compra='activo'):
        self.eventos = eventos
        self.estado_compra = estado_compra

    def execute(self, sql, params=None):
        self.eventos.append(('sql', ' '.join(sql.split()), params))

    def fetchone(self):
        return {'id': 5, 'estado_qr': self.estado_compra}

    def close(self):
        pass


class ConexionFalsa:
    def __init__(self, estado_compra='activo'):
        self.eventos = []
        self.estado_compra = estado_compra

    def cursor(self, dictionary=False):
        return CursorFalso(self.eventos, self.estado_compra)

    def commit(self):
        self.eventos.append(('commit',))

    def rollback(self):
        self.eventos.append(('rollback',))

    def close(self):
        pass


class CancelarLiberaButacasTests(unittest.TestCase):
    def _cancelar(self, estado_compra='activo'):
        conexion = ConexionFalsa(estado_compra)
        with patch.object(
            compras_repository, 'get_db_connection', return_value=conexion
        ):
            resultado = compras_repository.cancelar_compra_db(5)
        return resultado, conexion.eventos

    def test_al_cancelar_se_liberan_las_butacas_de_la_compra(self):
        resultado, eventos = self._cancelar()

        self.assertEqual(resultado[2], 200)
        liberacion = (
            'sql',
            'UPDATE entradas_detalle SET activa = NULL WHERE compra_id = %s',
            (5,),
        )
        self.assertIn(liberacion, eventos)
        # La liberación debe quedar dentro de la misma transacción que la cancelación.
        self.assertLess(eventos.index(liberacion), eventos.index(('commit',)))

    def test_una_compra_ya_cancelada_no_toca_las_butacas(self):
        resultado, eventos = self._cancelar(estado_compra='cancelado')

        self.assertEqual(resultado[2], 400)
        self.assertFalse(
            [e for e in eventos if e[0] == 'sql' and 'entradas_detalle' in e[1]]
        )


class EsquemaButacasTests(unittest.TestCase):
    def test_la_unicidad_de_butacas_solo_aplica_a_las_entradas_activas(self):
        esquema = SCHEMA.read_text(encoding='utf-8')

        self.assertIn('activa TINYINT(1) NULL DEFAULT 1', esquema)
        self.assertIn('UNIQUE (funcion_id, numero_butaca, activa)', esquema)
        self.assertNotIn('UNIQUE (funcion_id, numero_butaca)', esquema)


if __name__ == '__main__':
    unittest.main()
