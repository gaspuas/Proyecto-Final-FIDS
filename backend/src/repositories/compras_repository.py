import mysql.connector
from backend.src.utils.db_connection import get_db_connection

def obtener_usuario_por_id_db(id_usuario: int):
    connection = get_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, nombre, email, rol FROM usuarios WHERE id = %s",
            (id_usuario,)
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        connection.close()


def obtener_funcion_por_id_db(id_funcion: int):
    connection = get_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        sql = """
            SELECT
                f.id,
                f.sala_id,
                f.fecha_hora,
                f.precio_base,
                s.capacidad_total
            FROM funciones AS f
            INNER JOIN locales_salas AS s ON s.id = f.sala_id
            WHERE f.id = %s
        """
        cursor.execute(sql, (id_funcion,))
        return cursor.fetchone()
    finally:
        cursor.close()
        connection.close()


def obtener_servicio_por_id_db(id_servicio: int):
    connection = get_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, nombre, precio FROM servicios WHERE id = %s",
            (id_servicio,)
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        connection.close()


def obtener_butacas_ocupadas_db(id_funcion: int):
    connection = get_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        sql = """
            SELECT ed.numero_butaca
            FROM entradas_detalle AS ed
            INNER JOIN compras AS c ON c.id = ed.compra_id
            WHERE ed.funcion_id = %s
              AND c.estado_qr IN ('activo', 'usado')
        """
        cursor.execute(sql, (id_funcion,))
        return {str(fila['numero_butaca']) for fila in cursor.fetchall()}
    finally:
        cursor.close()
        connection.close()


def crear_compra_db(id_usuario: int, id_funcion: int, butacas: list,
                    servicios: list, precio_entrada, monto_total, codigo_qr: str):
    """Inserta compra, entradas y servicios en una única transacción."""
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO compras (usuario_id, monto_total, codigo_qr, estado_qr)
            VALUES (%s, %s, %s, 'activo')
            """,
            (id_usuario, monto_total, codigo_qr)
        )
        id_compra = cursor.lastrowid

        for numero_butaca in butacas:
            cursor.execute(
                """
                INSERT INTO entradas_detalle
                    (compra_id, funcion_id, numero_butaca, precio)
                VALUES (%s, %s, %s, %s)
                """,
                (id_compra, id_funcion, numero_butaca, precio_entrada)
            )

        for servicio in servicios:
            cursor.execute(
                """
                INSERT INTO compras_servicios
                    (compra_id, servicio_id, cantidad, precio_unitario)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    id_compra,
                    servicio['id'],
                    servicio['cant'],
                    servicio['precio_unitario']
                )
            )

        connection.commit()
        return id_compra
    except mysql.connector.Error:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


def obtener_compras_por_usuario_db(id_usuario: int):
    connection = get_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        sql = """
            SELECT
                c.id,
                c.usuario_id,
                c.fecha_compra,
                c.monto_total,
                c.codigo_qr,
                c.estado_qr
            FROM compras AS c
            WHERE c.usuario_id = %s
            ORDER BY c.fecha_compra DESC, c.id DESC
        """
        cursor.execute(sql, (id_usuario,))
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()


def obtener_entradas_por_compra_db(id_compra: int):
    connection = get_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        sql = """
            SELECT
                ed.id,
                ed.funcion_id,
                ed.numero_butaca,
                ed.precio,
                f.fecha_hora,
                f.sala_id
            FROM entradas_detalle AS ed
            INNER JOIN funciones AS f ON f.id = ed.funcion_id
            WHERE ed.compra_id = %s
            ORDER BY ed.id
        """
        cursor.execute(sql, (id_compra,))
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()


def obtener_servicios_por_compra_db(id_compra: int):
    connection = get_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        sql = """
            SELECT
                cs.servicio_id AS id,
                s.nombre,
                cs.cantidad AS cant,
                cs.precio_unitario,
                (cs.cantidad * cs.precio_unitario) AS subtotal
            FROM compras_servicios AS cs
            INNER JOIN servicios AS s ON s.id = cs.servicio_id
            WHERE cs.compra_id = %s
            ORDER BY cs.id
        """
        cursor.execute(sql, (id_compra,))
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()


def obtener_compra_por_id_db(id_compra: int):
    connection = get_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id, usuario_id, fecha_compra, monto_total, codigo_qr, estado_qr
            FROM compras
            WHERE id = %s
            """,
            (id_compra,)
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        connection.close()


def obtener_fecha_funcion_compra_db(id_compra: int):
    connection = get_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        sql = """
            SELECT MIN(f.fecha_hora) AS fecha_hora
            FROM entradas_detalle AS ed
            INNER JOIN funciones AS f ON f.id = ed.funcion_id
            WHERE ed.compra_id = %s
        """
        cursor.execute(sql, (id_compra,))
        fila = cursor.fetchone()
        return fila['fecha_hora'] if fila else None
    finally:
        cursor.close()
        connection.close()


def cancelar_compra_db(id_compra: int):
    """Actualiza el QR y marca los detalles como cancelados de forma atómica."""
    connection = get_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, estado_qr FROM compras WHERE id = %s FOR UPDATE",
            (id_compra,)
        )
        compra = cursor.fetchone()
        if not compra:
            connection.rollback()
            return None, "La compra no existe.", 404
        if compra['estado_qr'] != 'activo':
            connection.rollback()
            return None, "La compra no se encuentra activa.", 400

        cursor.execute(
            "UPDATE compras SET estado_qr = 'cancelado' WHERE id = %s",
            (id_compra,)
        )
        connection.commit()
        return {
            'id': id_compra,
            'estado_qr': 'cancelado'
        }, None, 200
    except mysql.connector.Error:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()
