"""Servicios adicionales, confirmacion, comprobante con QR, cancelacion e historial.

La reserva en curso la guarda reserva.procesar en session['checkout'].
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
from frontend.web.services.api_client import BackendAPIError
from frontend.web.services.funciones import obtener_funcion
from frontend.web.services.servicios import obtener_servicios
from frontend.web.sesion import (
    csrf_requerido,
    destino_seguro,
    login_requerido,
    usuario_actual,
)

compra_bp = Blueprint('compra', __name__)

CANTIDAD_MAXIMA = 10
PATRON_SERVICIO = re.compile(r'servicio_(\d+)')


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


def _checkout_en_curso():
    """Funcion y butacas (numeros como texto) elegidas en la reserva, o None."""
    checkout = session.get('checkout')
    if not isinstance(checkout, dict):
        return None
    id_funcion = checkout.get('id_funcion')
    butacas = checkout.get('butacas')
    if not isinstance(id_funcion, int) or id_funcion <= 0 or not isinstance(butacas, list):
        return None
    if not butacas or not all(isinstance(b, str) and b.isdigit() and int(b) > 0 for b in butacas):
        return None
    return checkout


def _volver_a_cartelera(mensaje):
    flash(mensaje, 'error')
    return redirect(url_for('web.site.peliculas.index'))


@compra_bp.route('/servicios')
@login_requerido
def servicios():
    checkout = _checkout_en_curso()
    if checkout is None:
        return _volver_a_cartelera('Elegí una función y tus butacas para continuar.')

    try:
        funcion = obtener_funcion(checkout['id_funcion'])
    except BackendAPIError as error:
        if error.status_code != 404:
            raise
        session.pop('checkout', None)
        return _volver_a_cartelera('La función elegida ya no está disponible.')

    try:
        catalogo = obtener_servicios()
        error_catalogo = None
    except BackendAPIError as error:
        catalogo = []
        error_catalogo = f'{error} Podés confirmar solo las entradas.'

    precio_entrada = _decimal(funcion.get('precio_base'))
    return render_template(
        'site/servicios.html',
        funcion=funcion,
        butacas=checkout['butacas'],
        precio_entrada=precio_entrada,
        total_entradas=precio_entrada * len(checkout['butacas']),
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
    checkout = _checkout_en_curso()
    if checkout is None:
        return _volver_a_cartelera('No hay una compra en curso. Elegí una función para empezar.')

    servicios_elegidos = _servicios_elegidos(request.form)
    if servicios_elegidos is None:
        flash(f'Las cantidades deben ser números entre 0 y {CANTIDAD_MAXIMA}.', 'error')
        return redirect(url_for('web.site.compra.servicios'))

    try:
        compra = compras.crear_compra(
            id_usuario=usuario_actual()['id'],
            id_funcion=checkout['id_funcion'],
            butacas=checkout['butacas'],
            servicios=servicios_elegidos,
        )
    except BackendAPIError as error:
        flash(str(error), 'error')
        return redirect(url_for('web.site.compra.servicios'))

    # Se descarta la reserva para que recargar o reenviar no repita la compra
    session.pop('checkout', None)
    if not isinstance(compra, dict) or not isinstance(compra.get('id'), int):
        return _volver_a_cartelera(
            'La compra se registró, pero no pudimos mostrar el comprobante. Revisá "Mis compras".'
        )
    flash('¡Listo! Tu compra quedó confirmada.', 'success')
    return redirect(url_for('web.site.compra.detalle', compra_id=compra['id']))


def _armar_comprobante(compra):
    entradas = compra.get('entradas') or []
    primera = entradas[0] if entradas else {}
    estado = compra.get('estado_qr')
    return {
        'id': compra['id'],
        'codigo': f"CP-{compra['id']:04d}",
        'estado': estado,
        'activa': estado == 'activo',
        'pelicula': primera.get('pelicula_titulo'),
        'sede': (
            f"{primera['nombre_local']} · Sala {primera['numero_sala']}"
            if primera.get('nombre_local') else None
        ),
        'fecha_hora': primera.get('fecha_hora'),
        'butacas': [str(entrada.get('numero_butaca')) for entrada in entradas],
        'total_entradas': sum((_decimal(entrada.get('precio')) for entrada in entradas), Decimal('0')),
        'servicios': compra.get('servicios') or [],
        'total': compra.get('monto_total'),
        'qr': _qr_data_uri(compra['codigo_qr']) if compra.get('codigo_qr') else None,
    }


@compra_bp.route('/<int:compra_id>')
@login_requerido
def detalle(compra_id):
    compra = compras.obtener_compra(usuario_actual()['id'], compra_id)
    if compra is None:
        abort(404)
    return render_template('site/confirmacion.html', compra=_armar_comprobante(compra))


@compra_bp.route('/<int:compra_id>/cancelar', methods=['POST'])
@login_requerido
@csrf_requerido
def cancelar(compra_id):
    try:
        # Antes de cancelar se verifica que la compra sea del usuario logueado
        if compras.obtener_compra(usuario_actual()['id'], compra_id) is None:
            abort(404)
        compras.cancelar_compra(compra_id)
    except BackendAPIError as error:
        flash(str(error), 'error')
    else:
        flash('Cancelamos tu compra. Las entradas ya no son válidas.', 'success')
    por_defecto = url_for('web.site.compra.detalle', compra_id=compra_id)
    return redirect(destino_seguro(request.form.get('next'), por_defecto))


@compra_bp.route('/historial')
@login_requerido
def historial():
    compras_usuario = compras.obtener_compras_usuario(usuario_actual()['id'])
    return render_template('site/historial_compras.html', compras=compras_usuario)
