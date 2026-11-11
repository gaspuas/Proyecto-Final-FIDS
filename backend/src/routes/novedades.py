"""Blueprint añadible a backend/app.py sin crear otra aplicación."""
from flask import Blueprint, current_app, jsonify, request
from backend.src.services import novedades_services as service
from backend.src.utils.novedades_auth import admin_novedades_required

novedades_bp = Blueprint("novedades", __name__, url_prefix="/api/novedades")


@novedades_bp.get("")
def listar():
    try:
        return jsonify(service.listar_publicas()), 200
    except Exception:
        current_app.logger.exception("Error consultando novedades")
        return jsonify({"error": "No se pudieron consultar las novedades"}), 503


@novedades_bp.get("/admin/todas")
@admin_novedades_required
def admin_listar():
    try:
        return jsonify(service.listar_todas())
    except Exception:
        current_app.logger.exception("Error listando novedades")
        return jsonify({"error": "Error al consultar novedades"}), 503


@novedades_bp.post("")
@admin_novedades_required
def crear():
    novedad, errores = service.crear_novedad(request.get_json(silent=True)) if request.is_json else (None, ["Se requiere JSON"])
    if errores:
        return jsonify({"errores": errores}), 400
    return jsonify(novedad), 201


@novedades_bp.put("/<int:novedad_id>")
@admin_novedades_required
def editar(novedad_id):
    novedad, errores = service.editar_novedad(novedad_id, request.get_json(silent=True)) if request.is_json else (None, ["Se requiere JSON"])
    if errores == ["No existe"]:
        return jsonify({"error": "No encontrada"}), 404
    if errores:
        return jsonify({"errores": errores}), 400
    return jsonify(novedad)


@novedades_bp.delete("/<int:novedad_id>")
@admin_novedades_required
def eliminar(novedad_id):
    if not service.eliminar_novedad(novedad_id):
        return jsonify({"error": "No encontrada"}), 404
    return "", 204
