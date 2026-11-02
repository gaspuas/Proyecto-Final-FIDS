from flask import Blueprint, jsonify, request

from backend.src.services.funciones_services import (
    consultar_butacas_funcion_service,
    listar_funciones_service,
)
from backend.src.utils.api_responses import generar_respuesta_error

funciones_bp = Blueprint('funciones', __name__, url_prefix='/api/funciones')


@funciones_bp.route('', methods=['GET'])
def listar_funciones():
    try:
        pelicula_id = request.args.get('pelicula_id')
        sala_id = request.args.get('sala_id')
        formato = request.args.get('formato')
        idioma = request.args.get('idioma')

        if pelicula_id is not None:
            try:
                pelicula_id = int(pelicula_id)
            except (TypeError, ValueError):
                pelicula_id = 'INVALID'

        if sala_id is not None:
            try:
                sala_id = int(sala_id)
            except (TypeError, ValueError):
                sala_id = 'INVALID'

        if formato is not None:
            formato = formato.strip()

        if idioma is not None:
            idioma = idioma.strip()

        funciones, err_negocio, status = listar_funciones_service(
            pelicula_id=pelicula_id,
            sala_id=sala_id,
            formato=formato,
            idioma=idioma,
        )

        if err_negocio:
            return generar_respuesta_error(
                'ERROR_VALIDACION',
                'Solicitud invalida',
                err_negocio,
                status,
            )

        return jsonify({'funciones': funciones}), 200

    except Exception as e:
        return generar_respuesta_error(
            'ERROR_INTERNO',
            'Error al listar las funciones',
            str(e),
            500,
        )


@funciones_bp.route('/<int:id_funcion>/butacas', methods=['GET'])
def consultar_butacas_funcion(id_funcion: int):
    try:
        mapa_butacas, err_negocio, status = consultar_butacas_funcion_service(id_funcion)

        if err_negocio:
            code = 'RECURSO_NO_ENCONTRADO' if status == 404 else 'ERROR_VALIDACION'
            message = 'Función no encontrada' if status == 404 else 'ID inválido'
            return generar_respuesta_error(code, message, err_negocio, status)

        return jsonify(mapa_butacas), 200

    except Exception as e:
        return generar_respuesta_error(
            'ERROR_INTERNO',
            'Error al consultar el mapa de butacas',
            str(e),
            500,
        )
