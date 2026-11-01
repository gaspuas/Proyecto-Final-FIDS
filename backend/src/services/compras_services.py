from datetime import datetime, timedelta
from decimal import Decimal
from secrets import token_urlsafe

import mysql.connector

from backend.src.repositories.compras_repository import *


HORAS_LIMITE_CANCELACION = 2


def _serializar_fecha(valor):
    if valor is None:
        return None
    if isinstance(valor, datetime):
        return valor.isoformat(sep=' ')
    return str(valor)


def _preparar_compra_response(compra):
    if not compra:
        return None
    compra_copy = dict(compra)
    if 'fecha_compra' in compra_copy:
        compra_copy['fecha_compra'] = _serializar_fecha(compra_copy['fecha_compra'])
    return compra_copy


def crear_compra_service(id_usuario: int, id_funcion: int, butacas: list, servicios: list):
    """
    Verifica usuario, función, butacas y servicios, calcula el total y registra
    la compra junto con sus detalles.
    Retorna (compra_creada, error_msg, status_code).
    """
    usuario = obtener_usuario_por_id_db(id_usuario)
    if not usuario:
        return None, f"Usuario con ID {id_usuario} no encontrado.", 400

    funcion = obtener_funcion_por_id_db(id_funcion)
    if not funcion:
        return None, f"Función con ID {id_funcion} no encontrada.", 400

    ahora = datetime.now()
    fecha_funcion = funcion['fecha_hora']
    if fecha_funcion <= ahora:
        return None, "No se pueden comprar entradas para una función que ya comenzó.", 400

    capacidad = int(funcion['capacidad_total'])
    butacas_invalidas = [
        butaca for butaca in butacas
        if not butaca.isdigit() or int(butaca) > capacidad
    ]
    if butacas_invalidas:
        return None, (
            "Las siguientes butacas no pertenecen a la capacidad de la sala: "
            + ", ".join(butacas_invalidas) + "."
        ), 400

    ocupadas = obtener_butacas_ocupadas_db(id_funcion)
    butacas_ocupadas = sorted(set(butacas) & ocupadas)
    if butacas_ocupadas:
        return None, (
            "Las siguientes butacas ya están ocupadas: "
            + ", ".join(butacas_ocupadas) + "."
        ), 400

    precio_entrada = Decimal(str(funcion['precio_base']))
    total = precio_entrada * len(butacas)
    servicios_con_precio = []

    for servicio in servicios:
        servicio_db = obtener_servicio_por_id_db(servicio['id'])
        if not servicio_db:
            return None, f"Servicio con ID {servicio['id']} no encontrado.", 400

        precio_unitario = Decimal(str(servicio_db['precio']))
        total += precio_unitario * servicio['cant']
        servicios_con_precio.append({
            'id': servicio['id'],
            'cant': servicio['cant'],
            'precio_unitario': precio_unitario
        })

    codigo_qr = token_urlsafe(32)

    try:
        id_compra = crear_compra_db(
            id_usuario=id_usuario,
            id_funcion=id_funcion,
            butacas=butacas,
            servicios=servicios_con_precio,
            precio_entrada=precio_entrada,
            monto_total=total,
            codigo_qr=codigo_qr
        )
    except mysql.connector.IntegrityError:
        # La restricción en la tabla UNIQUE(funcion_id, numero_butaca) no permite que varias solicitudes intenten comprar la misma butaca en simultáneo.
        return None, "Una o más butacas fueron reservadas por otra compra.", 400
    except mysql.connector.Error as e:
        return None, f"Error de base de datos al registrar la compra: {str(e)}", 500

    compra = obtener_compra_por_id_db(id_compra)
    compra = _preparar_compra_response(compra)
    compra['entradas'] = [
        {
            'funcion_id': id_funcion,
            'numero_butaca': butaca,
            'precio': float(precio_entrada)
        }
        for butaca in butacas
    ]
    compra['servicios'] = [
        {
            'id': item['id'],
            'cant': item['cant'],
            'precio_unitario': float(item['precio_unitario'])
        }
        for item in servicios_con_precio
    ]
    return compra, None, 201


def listar_compras_usuario_service(id_usuario: int):
    """
    Devuelve el historial de compras, incluyendo entradas y servicios.
    Retorna (compras, error_msg, status_code).
    """
    usuario = obtener_usuario_por_id_db(id_usuario)
    if not usuario:
        return None, f"Usuario con ID {id_usuario} no encontrado.", 400

    compras = obtener_compras_por_usuario_db(id_usuario)
    compras_response = []

    for compra in compras:
        compra = _preparar_compra_response(compra)
        compra['entradas'] = obtener_entradas_por_compra_db(compra['id'])
        compra['servicios'] = obtener_servicios_por_compra_db(compra['id'])

        for entrada in compra['entradas']:
            entrada['fecha_hora'] = _serializar_fecha(entrada['fecha_hora'])

        compras_response.append(compra)

    return compras_response, None, 200


def cancelar_compra_service(id_compra: int):
    """
    Comprueba existencia, estado y plazo de cancelación.
    Retorna (compra_actualizada, error_msg, status_code).
    """
    compra = obtener_compra_por_id_db(id_compra)
    if not compra:
        return None, f"Compra con ID {id_compra} no encontrada.", 404

    if compra['estado_qr'] != 'activo':
        return None, "La compra no se encuentra activa y no puede cancelarse.", 400

    fecha_funcion = obtener_fecha_funcion_compra_db(id_compra)
    if not fecha_funcion:
        return None, "La compra no tiene entradas asociadas a una función.", 400

    limite_cancelacion = fecha_funcion - timedelta(hours=HORAS_LIMITE_CANCELACION)
    if datetime.now() >= limite_cancelacion:
        return None, (
            f"La compra solo puede cancelarse hasta {HORAS_LIMITE_CANCELACION} "
            "horas antes del inicio de la función."
        ), 400

    try:
        compra_actualizada, error_msg, status = cancelar_compra_db(id_compra)
        if error_msg:
            return None, error_msg, status
        return compra_actualizada, None, 200
    except mysql.connector.Error as e:
        return None, f"Error de base de datos al cancelar la compra: {str(e)}", 500
