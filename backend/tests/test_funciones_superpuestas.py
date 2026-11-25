import unittest
from unittest.mock import patch

from backend.src.repositories import admin_repository
from backend.src.services import admin_services

DATOS_FUNCION = {
    'pelicula_id': 1,
    'sala_id': 2,
    'fecha_hora': '2026-12-01 18:00',
    'precio_base': 4500.0,
}


class CursorFalso:
    lastrowid = 99

    def __init__(self, eventos, superposicion):
        self.eventos = eventos
        self.superposicion = superposicion
        self.ultima_sql = ''

    def execute(self, sql, params=None):
        self.ultima_sql = ' '.join(sql.split())
        self.eventos.append(self.ultima_sql)

    def fetchone(self):
        if 'DATE_ADD' in self.ultima_sql:
            return self.superposicion
        return (2,)

    def close(self):
        pass


class ConexionFalsa:
    def __init__(self, superposicion=None):
        self.eventos = []
        self.superposicion = superposicion

    def cursor(self, dictionary=False):
        return CursorFalso(self.eventos, self.superposicion)

    def commit(self):
        self.eventos.append('commit')

    def rollback(self):
        self.eventos.append('rollback')

    def close(self):
        pass


class FuncionesSuperpuestasTests(unittest.TestCase):
    def _crear(self, superposicion=None):
        conexion = ConexionFalsa(superposicion)
        with patch.object(
            admin_repository, 'get_db_connection', return_value=conexion
        ):
            resultado = admin_services.crear_funcion_service(DATOS_FUNCION)
        return resultado, conexion.eventos

    def test_rechaza_una_funcion_superpuesta_en_la_misma_sala(self):
        (respuesta, error), eventos = self._crear(superposicion=(7,))

        self.assertIsNone(respuesta)
        self.assertEqual(error[0], 'CONFLICT')
        self.assertEqual(error[3], 409)
        self.assertFalse([e for e in eventos if e.startswith('INSERT')])
        self.assertIn('rollback', eventos)

    def test_crea_la_funcion_si_la_sala_esta_libre(self):
        (respuesta, error), eventos = self._crear()

        self.assertIsNone(error)
        self.assertEqual(respuesta['id'], 99)
        self.assertIn('commit', eventos)

    def test_bloquea_la_sala_antes_de_controlar_e_insertar(self):
        _, eventos = self._crear()

        bloqueo = next(i for i, e in enumerate(eventos) if 'FOR UPDATE' in e)
        control = next(i for i, e in enumerate(eventos) if 'DATE_ADD' in e)
        alta = next(i for i, e in enumerate(eventos) if e.startswith('INSERT'))
        self.assertLess(bloqueo, control)
        self.assertLess(control, alta)
        self.assertIn('f.sala_id = %s', eventos[control])


if __name__ == '__main__':
    unittest.main()
