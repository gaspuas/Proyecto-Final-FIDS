"""Persistencia de TokenSession. Solo se almacena el SHA-256 del token."""
from datetime import datetime, timezone
from hashlib import sha256

import mysql.connector

from backend.src.utils.db_connection import get_db_connection


def _hash_token(token: str) -> str:
    return sha256(token.encode('utf-8')).hexdigest()


def _conexion():
    conexion = get_db_connection()
    if conexion is None:
        raise mysql.connector.Error('No se pudo conectar a MySQL para validar la sesión.')
    return conexion


def registrar_sesion(usuario_id: int, token: str, expira_en: datetime):
    """Inserta una sesión con vencimiento UTC. Nunca persiste el token en claro."""
    conexion = _conexion()
    cursor = None
    try:
        cursor = conexion.cursor()
        cursor.execute(
            """INSERT INTO sesiones (usuario_id, token_hash, expira_en)
               VALUES (%s, %s, %s)""",
            (usuario_id, _hash_token(token), expira_en.astimezone(timezone.utc).replace(tzinfo=None)),
        )
        conexion.commit()
    except mysql.connector.Error:
        conexion.rollback()
        raise
    finally:
        if cursor is not None:
            cursor.close()
        conexion.close()


def buscar_usuario_por_token(token: str):
    """Identifica al usuario actual y rechaza tokens vencidos o revocados."""
    conexion = _conexion()
    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            """SELECT u.id, u.nombre, u.email, u.rol, s.expira_en
               FROM sesiones AS s
               INNER JOIN usuarios AS u ON u.id = s.usuario_id
               WHERE s.token_hash = %s AND s.revocado_en IS NULL""",
            (_hash_token(token),),
        )
        resultado = cursor.fetchone()
        if resultado is None:
            return None
        # La columna DATETIME se guarda en UTC (no en la zona horaria de MySQL).
        expira = resultado.pop('expira_en')
        if expira is None or expira <= datetime.now(timezone.utc).replace(tzinfo=None):
            return None
        return resultado
    finally:
        if cursor is not None:
            cursor.close()
        conexion.close()


def revocar_sesion(token_hash: str):
    """Logout: invalida inmediatamente este token, aun si la sesión web sigue viva."""
    conexion = _conexion()
    cursor = None
    try:
        cursor = conexion.cursor()
        cursor.execute(
            """UPDATE sesiones
               SET revocado_en = UTC_TIMESTAMP(6)
               WHERE token_hash = %s AND revocado_en IS NULL""",
            (token_hash,),
        )
        conexion.commit()
    except mysql.connector.Error:
        conexion.rollback()
        raise
    finally:
        if cursor is not None:
            cursor.close()
        conexion.close()
