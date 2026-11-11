import mysql.connector
from backend.src.utils.db_connection import get_db_connection


def obtener_funciones_db(
    pelicula_id: int | None = None,
    sala_id: int | None = None,
    formato: str | None = None,
    idioma: str | None = None,
):
    connection = get_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        sql = """
            SELECT
                f.id,
                f.pelicula_id,
                p.titulo AS pelicula_titulo,
                f.sala_id,
                s.nombre_local,
                s.numero_sala,
                s.capacidad_total,
                s.filas,
                s.columnas,
                f.fecha_hora,
                f.precio_base,
                f.formato,
                f.idioma
            FROM funciones AS f
            INNER JOIN peliculas AS p ON p.id = f.pelicula_id
            INNER JOIN locales_salas AS s ON s.id = f.sala_id
            WHERE f.fecha_hora >= NOW()
        """
        params = []

        if pelicula_id is not None:
            sql += " AND f.pelicula_id = %s"
            params.append(pelicula_id)

        if sala_id is not None:
            sql += " AND f.sala_id = %s"
            params.append(sala_id)

        if formato is not None:
            sql += " AND LOWER(TRIM(CAST(f.formato AS CHAR))) = LOWER(%s)"
            params.append(str(formato).strip())

        if idioma is not None:
            sql += " AND LOWER(TRIM(CAST(f.idioma AS CHAR))) = LOWER(%s)"
            params.append(str(idioma).strip())

        sql += " ORDER BY f.fecha_hora ASC, f.id ASC"

        cursor.execute(sql, tuple(params))
        return cursor.fetchall()
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
                f.pelicula_id,
                p.titulo AS pelicula_titulo,
                f.sala_id,
                s.nombre_local,
                s.numero_sala,
                s.capacidad_total,
                s.filas,
                s.columnas,
                f.fecha_hora,
                f.precio_base
            FROM funciones AS f
            INNER JOIN peliculas AS p ON p.id = f.pelicula_id
            INNER JOIN locales_salas AS s ON s.id = f.sala_id
            WHERE f.id = %s
        """
        cursor.execute(sql, (id_funcion,))
        return cursor.fetchone()
    finally:
        cursor.close()
        connection.close()


def obtener_butacas_ocupadas_db(id_funcion: int):
    connection = get_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        sql = """
            SELECT DISTINCT ed.numero_butaca
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
