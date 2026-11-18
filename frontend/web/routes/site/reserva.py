import re

from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for

from frontend.web.services.funciones import obtener_butacas, obtener_funcion

reserva_bp = Blueprint('reserva', __name__)

# Código de butaca: letra de fila + número de columna (A1, C7).
CODIGO_BUTACA = re.compile(r'[A-Z][1-9][0-9]?')


def _agrupar_por_fila(butacas):
    """Agrupa las butacas por letra de fila, conservando el orden del mapa."""
    filas = {}
    for butaca in butacas:
        filas.setdefault(butaca['fila'], []).append(butaca)
    return filas


def _render_reserva(funcion_id, seleccionadas=None):
    funcion = obtener_funcion(funcion_id)
    mapa = obtener_butacas(funcion_id)
    return render_template(
        'site/reserva_butacas.html',
        funcion=funcion,
        filas=_agrupar_por_fila(mapa['butacas']),
        columnas=range(1, mapa['columnas'] + 1),
        seleccionadas=seleccionadas or [],
    )


@reserva_bp.route('/<int:funcion_id>')
def butacas(funcion_id):
    return _render_reserva(funcion_id)


@reserva_bp.route('/butacas', methods=['POST'])
def procesar():
    try:
        funcion_id = int(request.form.get('funcion_id', ''))
    except ValueError:
        abort(400)

    if request.method == 'GET':
        return _render_reserva(funcion_id)

    asientos = request.form.getlist('asientos')
    if not asientos:
        return redirect(url_for('.butacas', funcion_id=funcion_id))
    if any(not CODIGO_BUTACA.fullmatch(asiento) for asiento in asientos):
        abort(400)
    if len(set(asientos)) != len(asientos):
        abort(400)

    mapa = obtener_butacas(funcion_id)
    libres = {butaca['codigo'] for butaca in mapa['butacas'] if butaca['libre']}
    if not set(asientos).issubset(libres):
        flash('Una o más butacas ya no están disponibles. Elegí otras.', 'error')
        return _render_reserva(funcion_id, seleccionadas=asientos)

    session['checkout'] = {'id_funcion': funcion_id, 'butacas': asientos}
    return redirect(url_for('web.site.compra.servicios'))
