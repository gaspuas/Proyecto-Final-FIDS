import mysql.connector
from flask import Blueprint, jsonify, request
from backend.src.services.funciones_services import *
from backend.src.utils.api_responses import *
from backend.src.utils.db_connection import get_db_connection
funciones_bp = Blueprint('funciones', __name__, url_prefix='/api/funciones')

@funciones_bp.route('/<int:id_funcion>', methods=['GET'])
def obtener_funcion(id_funcion: int):
    try:
        conexion = get_db_connection()
        cursor = conexion.cursor(dictionary=True)
        # Cambiamos la query quitando la columna 'fecha'
        query = """
            SELECT id, pelicula_id, sala_id, fecha_hora, precio_base, idioma, formato 
            FROM funciones 
            WHERE id = %s
        """
        cursor.execute(query, (id_funcion,))
        fila = cursor.fetchone()
        cursor.close()

        if not fila:
            return (
                jsonify({'error': f'Función {id_funcion} no encontrada'}),
                404,
            )

        fecha_dt = fila['fecha_hora']

        funcion_data = {
            'id': fila['id'],
            'pelicula_id': fila['pelicula_id'],
            'fecha_hora': str(fecha_dt),  # "2026-11-10 18:30:00"
            'hora': (
                fecha_dt.strftime('%H:%M')
                if hasattr(fecha_dt, 'strftime')
                else str(fecha_dt)[11:16]
            ),  # "18:30"
            'precio_base': float(fila['precio_base']),
        }

        return jsonify(funcion_data), 200

    except Exception as e:
        print(f'Error al consultar función en MySQL: {e}')
        return jsonify({'error': 'Error interno'}), 500
    finally:
        if conexion and conexion.is_connected():
            conexion.close()

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


@funciones_bp.route('/<int:id_funcion>/reservar', methods=['POST'])
def crear_reserva_funcion(id_funcion: int):
    try:
        data = request.get_json() or {}
        usuario_id = data.get('usuario_id')
        asientos = data.get('asientos', [])
        servicios = data.get('servicios', [])

        if not usuario_id or not asientos:
            return generar_respuesta_error(
                'ERROR_VALIDACION',
                'Faltan datos requeridos (usuario_id o asientos)',
                ['usuario_id y asientos son obligatorios'],
                400,
            )

        # Invocamos la lógica en la capa de servicios
        reserva, err_negocio, status = crear_reserva_service(
            usuario_id, id_funcion, asientos, servicios
        )

        if err_negocio:
            return generar_respuesta_error(
                'ERROR_RESERVA',
                'No se pudo completar la reserva',
                err_negocio,
                status,
            )

        return jsonify(reserva), 201

    except Exception as e:
        return generar_respuesta_error(
            'ERROR_INTERNO',
            'Error al procesar la reserva',
            str(e),
            500,
        )