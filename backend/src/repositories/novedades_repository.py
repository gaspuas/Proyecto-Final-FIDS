"""Consultas SQL explícitas. Reutiliza la conexión que ya tiene Cine Paradiso."""
from backend.src.utils.db_connection import get_db_connection

CAMPOS = ("titulo", "descripcion", "imagen_url", "tipo", "enlace", "orden",
          "fecha_inicio", "fecha_fin", "activo")


def _consultar(sql, params=(), uno=False):
    conn = get_db_connection()
    if conn is None:
        raise RuntimeError("No se pudo conectar con MySQL")
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params)
        return cursor.fetchone() if uno else cursor.fetchall()
    finally:
        if cursor is not None:
            cursor.close()
        conn.close()


def listar_publicables():
    return _consultar("""
        SELECT id, titulo, descripcion, imagen_url, tipo, enlace, orden
        FROM novedades
        WHERE activo = 1
          AND (fecha_inicio IS NULL OR fecha_inicio <= NOW())
          AND (fecha_fin IS NULL OR fecha_fin >= NOW())
        ORDER BY orden ASC, id ASC
    """)


def listar_todas():
    return _consultar("SELECT * FROM novedades ORDER BY orden ASC, id ASC")


def obtener_por_id(novedad_id):
    return _consultar("SELECT * FROM novedades WHERE id = %s", (novedad_id,), uno=True)


def _escribir(sql, params=(), devolver_id=False):
    conn = get_db_connection()
    if conn is None:
        raise RuntimeError("No se pudo conectar con MySQL")
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        resultado = cursor.lastrowid if devolver_id else cursor.rowcount
        conn.commit()
        return resultado
    except Exception:
        conn.rollback()
        raise
    finally:
        if cursor is not None:
            cursor.close()
        conn.close()


def crear(datos):
    columnas = [c for c in CAMPOS if c in datos]
    if not columnas:
        raise ValueError("No hay datos para crear")
    sql = ("INSERT INTO novedades (" + ", ".join(columnas) + ") VALUES (" +
           ", ".join(["%s"] * len(columnas)) + ")")
    return _escribir(sql, tuple(datos[c] for c in columnas), devolver_id=True)


def actualizar(novedad_id, datos):
    columnas = [c for c in CAMPOS if c in datos]
    if not columnas:
        return 0
    sql = "UPDATE novedades SET " + ", ".join(c + " = %s" for c in columnas) + " WHERE id = %s"
    return _escribir(sql, tuple(datos[c] for c in columnas) + (novedad_id,))


def eliminar(novedad_id):
    return _escribir("DELETE FROM novedades WHERE id = %s", (novedad_id,)) > 0
