"""Reglas de negocio del carrusel."""
from backend.src.repositories import novedades_repository as repo
from backend.src.validators.novedades_validators import validar_novedad


def listar_publicas():
    return repo.listar_publicables()


def listar_todas():
    return repo.listar_todas()


def crear_novedad(data):
    limpio, errores = validar_novedad(data)
    if errores:
        return None, errores
    return repo.obtener_por_id(repo.crear(limpio)), []


def editar_novedad(novedad_id, data):
    actual = repo.obtener_por_id(novedad_id)
    if actual is None:
        return None, ["No existe"]
    limpio, errores = validar_novedad(data, parcial=True)
    if errores:
        return None, errores
    # Validar fechas considerando también las que no cambian.
    inicio = limpio.get("fecha_inicio", actual.get("fecha_inicio"))
    fin = limpio.get("fecha_fin", actual.get("fecha_fin"))
    if inicio is not None and fin is not None and str(inicio) > str(fin):
        return None, ["fecha_fin debe ser posterior o igual a fecha_inicio"]
    repo.actualizar(novedad_id, limpio)
    return repo.obtener_por_id(novedad_id), []


def eliminar_novedad(novedad_id):
    return repo.eliminar(novedad_id)
