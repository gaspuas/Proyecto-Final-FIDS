import uuid
from datetime import datetime

from backend.src.repositories.funciones_repository import *



def _serializar_fecha(valor):
    if valor is None:
        return None
    if isinstance(valor, datetime):
        return valor.isoformat(sep=' ')
    return str(valor)


def _serializar_funcion(funcion):
    if not funcion:
        return None
    funcion_serializada = dict(funcion)
    if 'fecha_hora' in funcion_serializada:
        funcion_serializada['fecha_hora'] = _serializar_fecha(funcion_serializada['fecha_hora'])
    return funcion_serializada


def listar_funciones_service(
    pelicula_id: int | None = None,
    sala_id: int | None = None,
    formato: str | None = None,
    idioma: str | None = None,
):
    """Devuelve las funciones vigentes con filtros opcionales."""
    if pelicula_id is not None:
        if not isinstance(pelicula_id, int) or isinstance(pelicula_id, bool) or pelicula_id <= 0:
            return None, "El campo 'pelicula_id' debe ser un entero positivo.", 400

    if sala_id is not None:
        if not isinstance(sala_id, int) or isinstance(sala_id, bool) or sala_id <= 0:
            return None, "El campo 'sala_id' debe ser un entero positivo.", 400

    if formato is not None:
        if not isinstance(formato, str):
            return None, "El campo 'formato' debe ser un texto válido.", 400
        formato = formato.strip()
        if not formato:
            return None, "El campo 'formato' no puede estar vacío.", 400

    if idioma is not None:
        if not isinstance(idioma, str):
            return None, "El campo 'idioma' debe ser un texto válido.", 400
        idioma = idioma.strip()
        if not idioma:
            return None, "El campo 'idioma' no puede estar vacío.", 400

    funciones = obtener_funciones_db(
        pelicula_id=pelicula_id,
        sala_id=sala_id,
        formato=formato,
        idioma=idioma,
    )
    funciones_response = [
        _serializar_funcion(funcion) for funcion in funciones
    ]
    return funciones_response, None, 200



def crear_reserva_service(usuario_id: int, id_funcion: int, asientos: list, servicios: list):
    """Crea una reserva en MySQL registrando cabecera, asientos y combos opcionales."""
    # 1. Validaciones básicas de entrada
    if not isinstance(id_funcion, int) or id_funcion <= 0:
        return None, "El ID de la función debe ser un entero positivo.", 400

    if not asientos or not isinstance(asientos, list):
        return None, "Debe seleccionar al menos un asiento.", 400

    # 2. Verificar existencia de la función
    funcion = obtener_funcion_por_id_db(id_funcion)
    if not funcion:
        return None, f"Función con ID {id_funcion} no encontrada.", 404

    # 3. Comprobar solapamiento de butacas ocupadas
    ocupadas_db = obtener_butacas_ocupadas_db(id_funcion)
    # Convertimos a string por seguridad para comparar (ej: '1' o 'A1')
    ocupadas_set = {str(b) for b in ocupadas_db}
    solapadas = [a for a in asientos if str(a) in ocupadas_set]

    if solapadas:
        return None, f"Las siguientes butacas ya están ocupadas: {', '.join(map(str, solapadas))}", 409

    # 4. Transacción e inserción en MySQL
    cursor = mysql.connection.cursor()
    try:
        codigo_reserva = f"RES-{id_funcion}-{uuid.uuid4().hex[:6].upper()}"

        # A. Insertar cabecera de reserva
        query_reserva = """
            INSERT INTO reservas (usuario_id, funcion_id, codigo_reserva, estado)
            VALUES (%s, %s, %s, 'CONFIRMADA')
        """
        cursor.execute(query_reserva, (usuario_id, id_funcion, codigo_reserva))
        reserva_id = cursor.lastrowid

        # B. Insertar cada asiento reservado
        query_asiento = """
            INSERT INTO reserva_asientos (reserva_id, codigo_asiento)
            VALUES (%s, %s)
        """
        for asiento in asientos:
            cursor.execute(query_asiento, (reserva_id, str(asiento)))

        # C. Insertar servicios opcionales (Candy Bar)
        if servicios:
            query_servicio = """
                INSERT INTO reserva_servicios (reserva_id, servicio_id, cantidad, precio_unitario)
                VALUES (%s, %s, %s, %s)
            """
            for s in servicios:
                cursor.execute(
                    query_servicio,
                    (
                        reserva_id,
                        s.get('id'),
                        s.get('cantidad', 1),
                        s.get('precio', 0.0)
                    )
                )

        mysql.connection.commit()
        cursor.close()

        # 5. Cálculo de totales y respuesta de éxito
        precio_unitario = float(funcion.get('precio_entrada', 4500.0))
        total_entradas = len(asientos) * precio_unitario
        total_servicios = sum(float(s.get('precio', 0)) * int(s.get('cantidad', 1)) for s in servicios)

        resultado = {
            'compra': {
                'codigo': codigo_reserva,
                'pelicula': funcion.get('pelicula', 'Película Seleccionada'),
                'fecha_hora': f"{funcion.get('fecha', 'Hoy')} {funcion.get('horario', '19:30 hs')}",
                'butacas': asientos
            },
            'total_entradas': total_entradas,
            'elegidos': servicios,
            'total': total_entradas + total_servicios
        }

        return resultado, None, 201

    except Exception as e:
        mysql.connection.rollback()
        cursor.close()
        raise e

def consultar_butacas_funcion_service(id_funcion: int):
    if (
        not isinstance(id_funcion, int)
        or isinstance(id_funcion, bool)
        or id_funcion <= 0
    ):
        return None, 'El ID de la función debe ser un entero positivo.', 400

    funcion = obtener_funcion_por_id_db(id_funcion)
    if not funcion:
        return None, f'Función con ID {id_funcion} no encontrada.', 404

    # Obtenemos la lista directa de códigos string guardados en MySQL (ej: ['A1', 'A2'])
    ocupadas_lista = [str(b) for b in obtener_butacas_ocupadas_db(id_funcion)]

    return {
        'funcion_id': id_funcion,
        'ocupadas': ocupadas_lista,
    }, None, 200
