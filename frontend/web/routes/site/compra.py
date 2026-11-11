"""Frontend routes for the database-backed checkout flow."""
from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for

from frontend.web.services.api_client import BackendAPIError
from frontend.web.services.compras import (
    cancelar_compra,
    crear_compra,
    obtener_compras_usuario,
)
from frontend.web.services.funciones import obtener_funcion
from frontend.web.services.servicios import obtener_servicios

compra_bp = Blueprint('compra', __name__)
CANTIDAD_MAXIMA = 10


def _checkout():
    checkout = session.get('checkout')
    if not checkout or not checkout.get('id_funcion') or not checkout.get('butacas'):
        flash('Primero elegí una función y sus butacas.', 'error')
        return None
    return checkout


def _require_login():
    if session.get('usuario'):
        return True
    flash('Iniciá sesión para continuar con la compra.', 'error')
    return False


@compra_bp.route('/servicios', methods=['GET', 'POST'])
def servicios():
    checkout = _checkout()
    if checkout is None:
        return redirect(url_for('web.site.peliculas.index'))
    if not _require_login():
        return redirect(url_for('web.site.login.index', next=request.path))

    funcion = obtener_funcion(checkout['id_funcion'])
    servicios_disponibles = obtener_servicios()
    total_entradas = float(funcion['precio_base']) * len(checkout['butacas'])
    datos_vista = {
        'funcion': funcion,
        'butacas': checkout['butacas'],
        'servicios': servicios_disponibles,
        'cantidad_maxima': CANTIDAD_MAXIMA,
        'total_entradas': total_entradas,
    }

    if request.method == 'GET':
        return render_template('site/servicios.html', **datos_vista, error=None)

    servicios_elegidos = []
    cantidades_por_id = {}
    for servicio in servicios_disponibles:
        campo = f"servicio_{servicio['id']}"
        try:
            cantidad = int(request.form.get(campo, '0'))
        except ValueError:
            cantidad = -1
        if cantidad < 0 or cantidad > CANTIDAD_MAXIMA:
            return render_template(
                'site/servicios.html',
                **datos_vista,
                error=f'La cantidad de {servicio["nombre"]} debe estar entre 0 y {CANTIDAD_MAXIMA}.',
            ), 400
        cantidades_por_id[servicio['id']] = cantidad
        if cantidad:
            servicios_elegidos.append({'id': int(servicio['id']), 'cant': cantidad})

    compra = crear_compra(
        id_usuario=int(session['usuario']['id']),
        id_funcion=int(checkout['id_funcion']),
        butacas=checkout['butacas'],
        servicios=servicios_elegidos,
    )

    compra_id = compra.get('id')
    if not compra_id:
        raise BackendAPIError('La API no devolvió el identificador de la compra.')

    compra['pelicula'] = funcion['pelicula_titulo']
    compra['fecha_hora'] = funcion['fecha_hora']
    compra['butacas'] = checkout['butacas']
    compra['total_entradas'] = total_entradas
    compra['total'] = float(compra.get('monto_total', 0))
    compra['servicios_elegidos'] = [
        {
            **servicio,
            'cantidad': cantidades_por_id[servicio['id']],
            'subtotal': float(servicio['precio']) * cantidades_por_id[servicio['id']],
        }
        for servicio in servicios_disponibles
        if cantidades_por_id[servicio['id']]
    ]
    session.pop('checkout', None)
    return render_template('site/confirmacion.html', compra=compra)


@compra_bp.route('/<int:compra_id>/cancelar', methods=['POST'])
def cancelar(compra_id):
    usuario = session.get('usuario')
    if not usuario:
        return redirect(url_for('web.site.login.index'))
    compras_usuario = obtener_compras_usuario(int(usuario['id']))
    if not any(compra['id'] == compra_id for compra in compras_usuario):
        abort(404)

    cancelar_compra(compra_id)
    flash('La compra fue cancelada.', 'success')
    return redirect(url_for('.historial'))


@compra_bp.route('/historial')
def historial():
    usuario = session.get('usuario')
    if not usuario:
        flash('Iniciá sesión para consultar tus compras.', 'error')
        return redirect(url_for('web.site.login.index', next=request.path))
    compras_usuario = obtener_compras_usuario(int(usuario['id']))
    return render_template('site/historial_compras.html', compras=compras_usuario)
