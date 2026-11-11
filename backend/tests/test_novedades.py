"""Pruebas sin MySQL real ni frameworks extra (python -m unittest discover -s tests)."""
import unittest
import sys
from types import ModuleType
# El conector real pertenece al proyecto principal. Sustitución solo para estas pruebas.
if "backend.src.utils.db_connection" not in sys.modules:
    stub = ModuleType("backend.src.utils.db_connection")
    def _not_connected():
        raise RuntimeError("DB simulada: conectar en el proyecto real")
    stub.get_db_connection = _not_connected
    sys.modules["backend.src.utils.db_connection"] = stub
from datetime import datetime, timedelta
from unittest.mock import patch
from backend.src.validators.novedades_validators import validar_novedad
from backend.src.services import novedades_services as service

class ValidacionTests(unittest.TestCase):
    def test_crear_valido(self):
        dato = {"titulo": "Estreno", "imagen_url": "/static/img/prueba.webp", "tipo": "estreno", "orden": 0, "activo": True}
        result, errors = validar_novedad(dato)
        self.assertFalse(errors)
        self.assertEqual(result["activo"], 1)

    def test_no_acepta_url_javascript(self):
        result, errors = validar_novedad({"titulo": "X", "imagen_url": "javascript:alert(1)", "tipo": "estreno"})
        self.assertTrue(errors)

    def test_rechaza_orden_booleano(self):
        _, errors = validar_novedad({"titulo": "X", "imagen_url": "/a", "tipo": "oferta", "orden": True})
        self.assertTrue(errors)

    def test_rechaza_fechas_invertidas(self):
        _, errors = validar_novedad({"titulo": "X", "imagen_url": "/a", "tipo": "oferta", "fecha_inicio": "2027-01-02", "fecha_fin": "2027-01-01"})
        self.assertTrue(errors)

    def test_tipo_invalido(self):
        _, errors = validar_novedad({"titulo": "X", "imagen_url": "/a", "tipo": "otro"})
        self.assertTrue(errors)

    def test_publicas_devuelve_coleccion(self):
        novedad = {"id":1, "titulo":"A", "descripcion":"", "imagen_url":"/a", "tipo":"oferta", "enlace":"/cartelera", "orden":1}
        with patch.object(service.repo, "listar_publicables", return_value=[novedad]):
            self.assertEqual(service.listar_publicas(), [novedad])

if __name__ == "__main__":
    unittest.main()
