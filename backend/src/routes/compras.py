from flask import Blueprint, current_app, request, jsonify

from backend.src.utils.api_responses import generar_respuesta_error
from backend.src.validators.compras_validators import (
    validar_body_crear_compra,
    validar_id_recurso,
)
from backend.src.services.compras_services import (
    crear_compra_service,
    listar_compras_usuario_service,
    cancelar_compra_service,
)
from backend.src.utils.qr_generator import generar_qr_base64

compras_bp = Blueprint('compras', __name__, url_prefix='/api/compras')


@compras_bp.route('', methods=['POST'])
def crear_compra():
    try:
        data = request.get_json(silent=True)
        datos_compra, error_msg = validar_body_crear_compra(data)
        if error_msg:
            return generar_respuesta_error(
                "ERROR_VALIDACION", "Solicitud invalida", error_msg, 400
            )

        compra, err_negocio, status = crear_compra_service(**datos_compra)
        if err_negocio:
            code = "RECURSO_NO_ENCONTRADO" if status == 404 else "CONFLICTO_NEGOCIO"
            msg = "Recurso no encontrado" if status == 404 else "No se pudo crear la compra"
            return generar_respuesta_error(code, msg, err_negocio, status)

        compra['qr_data_uri'] = generar_qr_base64(compra['codigo_qr'])
        return jsonify(compra), 201

    except Exception as e:
        current_app.logger.exception("Error al crear compra")
        return generar_respuesta_error(
            "ERROR_INTERNO", "Error al crear la compra", str(e), 500
        )


@compras_bp.route('/usuario/<int:id_usuario>', methods=['GET'])
def listar_compras_usuario(id_usuario: int):
    try:
        valido, error_msg = validar_id_recurso(id_usuario)
        if not valido:
            return generar_respuesta_error(
                "ERROR_VALIDACION", "ID inválido", error_msg, 400
            )

        compras, err_negocio, status = listar_compras_usuario_service(id_usuario)
        if err_negocio:
            return generar_respuesta_error(
                "RECURSO_NO_ENCONTRADO", "Usuario no encontrado", err_negocio, status
            )

        return jsonify({"compras": compras}), 200

    except Exception as e:
        return generar_respuesta_error(
            "ERROR_INTERNO", "Error al consultar las compras del usuario", str(e), 500
        )


@compras_bp.route('/<int:id_compra>/cancelar', methods=['PATCH'])
def cancelar_compra(id_compra: int):
    try:
        valido, error_msg = validar_id_recurso(id_compra)
        if not valido:
            return generar_respuesta_error(
                "ERROR_VALIDACION", "ID invalido", error_msg, 400
            )

        compra, err_negocio, status = cancelar_compra_service(id_compra)
        if err_negocio:
            code = "RECURSO_NO_ENCONTRADO" if status == 404 else "CONFLICTO_NEGOCIO"
            msg = "Compra no encontrada" if status == 404 else "No se pudo cancelar la compra"
            return generar_respuesta_error(code, msg, err_negocio, status)

        return jsonify(compra), 200

    except Exception as e:
        return generar_respuesta_error(
            "ERROR_INTERNO", "Error al cancelar la compra", str(e), 500
        )
