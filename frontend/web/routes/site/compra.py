"""Servicios adicionales, confirmacion y cancelacion de compras.

Los importes que se muestran como definitivos salen siempre de la API.
"""
import base64
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation

import qrcode
import qrcode.image.svg
from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from frontend.web.services import compras
from frontend.web.services.api import ErrorApi
from frontend.web.sesion import csrf_requerido, login_requerido, usuario_actual

compra_bp = Blueprint('compra', __name__)

CANTIDAD_MAXIMA = 10

# La API numera las butacas de 1 a capacidad_total. La grilla de
# reserva_butacas.html usa filas A, B, C... de 10 butacas cada una.
BUTACAS_POR_FILA = 10
PATRON_BUTACA = re.compile(r'([A-Z])(\d{1,2})')
PATRON_SERVICIO = re.compile(r'servicio_(\d+)')


def codigo_a_numero(codigo):
    """'C5' -> 25. Devuelve None si el codigo no es valido."""
    coincidencia = PATRON_BUTACA.fullmatch(codigo or '')
    if not coincidencia:
        return None
    fila = ord(coincidencia.group(1)) - ord('A')
    columna = int(coincidencia.group(2))
    if not 1 <= columna <= BUTACAS_POR_FILA:
        return None
    return fila * BUTACAS_POR_FILA + columna


def numero_a_codigo(numero):
    """25 -> 'C5'."""
    try:
        indice = int(numero) - 1
    except (TypeError, ValueError):
        return str(numero)
    if indice < 0:
        return str(numero)
    fila, columna = divmod(indice, BUTACAS_POR_FILA)
    return f'{chr(ord("A") + fila)}{columna + 1}'


def _decimal(valor):
    try:
        return Decimal(str(valor))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal('0')


@compra_bp.app_template_filter('importe')
def formato_importe(valor):
    """4500.00 -> '4500'; 4500.50 -> '4500.50'."""
    importe = _decimal(valor).quantize(Decimal('0.01'))
    if importe == importe.to_integral_value():
        return str(int(importe))
    return str(importe)


@compra_bp.app_template_filter('precio')
def formato_precio(valor):
    return f'${formato_importe(valor)}'


@compra_bp.app_template_filter('fecha_hora')
def formato_fecha_hora(valor):
    try:
        return datetime.fromisoformat(str(valor)).strftime('%d/%m/%Y %H:%M hs')
    except ValueError:
        return valor


def _qr_data_uri(codigo_qr):
    imagen = qrcode.make(codigo_qr, image_factory=qrcode.image.svg.SvgPathImage, border=3)
    svg = imagen.to_string()
    return 'data:image/svg+xml;base64,' + base64.b64encode(svg).decode('ascii')


def _reserva_en_curso():
    """Funcion y butacas elegidas en la pantalla de reserva, o None."""
    reserva = session.get('reserva_temp')
    if not isinstance(reserva, dict):
        return None
    funcion_id = reserva.get('funcion_id')
    asientos = reserva.get('asientos')
    if not isinstance(funcion_id, int) or funcion_id <= 0 or not isinstance(asientos, list):
        return None
    if not asientos or any(codigo_a_numero(asiento) is None for asiento in asientos):
        return None
    return {'funcion_id': funcion_id, 'asientos': asientos}


def _pagina_no_disponible(mensaje):
    return render_template(
        '500.html', error_title='503 · Servicio no disponible', error_message=mensaje
    ), 503


def _volver_a_cartelera(mensaje):
    flash(mensaje, 'error')
    return redirect(url_for('web.site.peliculas.index'))


@compra_bp.route('/iniciar', methods=['POST'])
def iniciar():
    """Recibe el formulario de reserva_butacas.html (funcion_id y asientos)."""
    try:
        funcion_id = int(request.form.get('funcion_id', ''))
    except ValueError:
        funcion_id = 0
    asientos = list(dict.fromkeys(request.form.getlist('asientos')))

    if funcion_id <= 0:
        return _volver_a_cartelera('Elegí una función para continuar.')
    if not asientos or any(codigo_a_numero(asiento) is None for asiento in asientos):
        flash('Elegí al menos una butaca válida.', 'error')
        return redirect(url_for('web.site.reserva.butacas', funcion_id=funcion_id))

    session['reserva_temp'] = {'funcion_id': funcion_id, 'asientos': asientos}
    return redirect(url_for('web.site.compra.servicios'))


@compra_bp.route('/servicios')
@login_requerido
def servicios():
    reserva = _reserva_en_curso()
    if reserva is None:
        return _volver_a_cartelera('Elegí una función y tus butacas para continuar.')

    try:
        funcion = compras.obtener_funcion(reserva['funcion_id'])
    except ErrorApi as error:
        return _pagina_no_disponible(error.mensaje)
    if funcion is None:
        session.pop('reserva_temp', None)
        return _volver_a_cartelera('La función elegida ya no está disponible.')

    try:
        catalogo = compras.listar_servicios()
        error_catalogo = None
    except ErrorApi as error:
        catalogo = []
        error_catalogo = f'{error.mensaje} Podés confirmar solo las entradas.'

    precio_entrada = _decimal(funcion.get('precio_base'))
    return render_template(
        'site/servicios.html',
        funcion=funcion,
        butacas=reserva['asientos'],
        precio_entrada=precio_entrada,
        total_entradas=precio_entrada * len(reserva['asientos']),
        servicios=catalogo,
        error_catalogo=error_catalogo,
        cantidad_maxima=CANTIDAD_MAXIMA,
    )


def _servicios_elegidos(formulario):
    """Lista [{'id', 'cant'}] con las cantidades mayores a cero, o None si alguna es invalida."""
    elegidos = []
    for clave, valor in formulario.items():
        coincidencia = PATRON_SERVICIO.fullmatch(clave)
        if not coincidencia:
            continue
        valor = valor.strip() or '0'
        if not valor.isdecimal() or int(valor) > CANTIDAD_MAXIMA:
            return None
        if int(valor) > 0:
            elegidos.append({'id': int(coincidencia.group(1)), 'cant': int(valor)})
    return elegidos


@compra_bp.route('/confirmar', methods=['POST'])
@login_requerido
@csrf_requerido
def confirmar():
    reserva = _reserva_en_curso()
    if reserva is None:
        return _volver_a_cartelera('No hay una compra en curso. Elegí una función para empezar.')

    servicios_elegidos = _servicios_elegidos(request.form)
    if servicios_elegidos is None:
        flash(f'Las cantidades deben ser números entre 0 y {CANTIDAD_MAXIMA}.', 'error')
        return redirect(url_for('web.site.compra.servicios'))

    try:
        compra = compras.crear_compra(
            id_usuario=usuario_actual()['id'],
            id_funcion=reserva['funcion_id'],
            butacas=[str(codigo_a_numero(asiento)) for asiento in reserva['asientos']],
            servicios=servicios_elegidos,
        )
    except ErrorApi as error:
        flash(error.mensaje, 'error')
        return redirect(url_for('web.site.compra.servicios'))

    # Se descarta la reserva para que recargar o reenviar no repita la compra
    session.pop('reserva_temp', None)
    if not isinstance(compra.get('id'), int):
        return _volver_a_cartelera(
            'La compra se registró, pero no pudimos mostrar el comprobante. Revisá tus compras más tarde.'
        )
    flash('¡Listo! Tu compra quedó confirmada.', 'success')
    return redirect(url_for('web.site.compra.detalle', compra_id=compra['id']))


def _armar_comprobante(compra, funcion):
    entradas = compra.get('entradas') or []
    estado = compra.get('estado_qr')
    return {
        'id': compra['id'],
        'codigo': f"CP-{compra['id']:04d}",
        'estado': estado,
        'activa': estado == 'activo',
        'pelicula': funcion.get('pelicula_titulo') if funcion else None,
        'sede': f"{funcion['nombre_local']} · Sala {funcion['numero_sala']}" if funcion else None,
        'fecha_hora': entradas[0].get('fecha_hora') if entradas else None,
        'butacas': [numero_a_codigo(entrada.get('numero_butaca')) for entrada in entradas],
        'total_entradas': sum((_decimal(entrada.get('precio')) for entrada in entradas), Decimal('0')),
        'servicios': compra.get('servicios') or [],
        'total': compra.get('monto_total'),
        'qr': _qr_data_uri(compra['codigo_qr']) if compra.get('codigo_qr') else None,
    }


@compra_bp.route('/<int:compra_id>')
@login_requerido
def detalle(compra_id):
    try:
        compra = compras.obtener_compra(usuario_actual()['id'], compra_id)
    except ErrorApi as error:
        return _pagina_no_disponible(error.mensaje)
    if compra is None:
        abort(404)

    funcion = None
    entradas = compra.get('entradas') or []
    if entradas:
        try:
            # Solo se encuentra si la funcion todavia no paso
            funcion = compras.obtener_funcion(entradas[0].get('funcion_id'))
        except ErrorApi:
            funcion = None

    return render_template('site/confirmacion.html', compra=_armar_comprobante(compra, funcion))


@compra_bp.route('/<int:compra_id>/cancelar', methods=['POST'])
@login_requerido
@csrf_requerido
def cancelar(compra_id):
    try:
        # Antes de cancelar se verifica que la compra sea del usuario logueado
        if compras.obtener_compra(usuario_actual()['id'], compra_id) is None:
            abort(404)
        compras.cancelar_compra(compra_id)
    except ErrorApi as error:
        flash(error.mensaje, 'error')
    else:
        flash('Cancelamos tu compra. Las entradas ya no son válidas.', 'success')
    return redirect(url_for('web.site.compra.detalle', compra_id=compra_id))
