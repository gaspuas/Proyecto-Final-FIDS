"""Pantallas de servicios adicionales y confirmacion (solo frontend).

Todo usa datos de ejemplo: no se llama a la API ni se registra ninguna compra.
"""
from flask import Blueprint, render_template, request

compra_bp = Blueprint('compra', __name__)

CANTIDAD_MAXIMA = 10

COMPRA_EJEMPLO = {
    'pelicula': 'Cinema Paradiso',
    'fecha_hora': '05/11/2026 20:00 hs',
    'butacas': ['C5', 'C6'],
    'precio_butaca': 4500,
    'codigo': 'CP-0042',
}

# Mismo catalogo que la carga inicial de database/schema.sql
SERVICIOS_EJEMPLO = [
    {'id': 1, 'nombre': 'Combo Pochoclos + Bebida', 'precio': 4500},
    {'id': 2, 'nombre': 'Estacionamiento (3 horas)', 'precio': 2000},
    {'id': 3, 'nombre': 'Acceso Sala VIP', 'precio': 1500},
]


def _total_entradas():
    return COMPRA_EJEMPLO['precio_butaca'] * len(COMPRA_EJEMPLO['butacas'])


def _leer_cantidad(servicio):
    try:
        cantidad = int(request.args.get(f"servicio_{servicio['id']}", 0))
    except ValueError:
        return 0
    return max(0, min(cantidad, CANTIDAD_MAXIMA))


@compra_bp.route('/servicios')
def servicios():
    return render_template(
        'site/servicios.html',
        compra=COMPRA_EJEMPLO,
        servicios=SERVICIOS_EJEMPLO,
        total_entradas=_total_entradas(),
        cantidad_maxima=CANTIDAD_MAXIMA,
    )


@compra_bp.route('/confirmacion')
def confirmacion():
    elegidos = []
    for servicio in SERVICIOS_EJEMPLO:
        cantidad = _leer_cantidad(servicio)
        if cantidad > 0:
            elegidos.append({**servicio, 'cantidad': cantidad})

    total_servicios = sum(s['precio'] * s['cantidad'] for s in elegidos)

    return render_template(
        'site/confirmacion.html',
        compra=COMPRA_EJEMPLO,
        elegidos=elegidos,
        total_entradas=_total_entradas(),
        total=_total_entradas() + total_servicios,
    )
