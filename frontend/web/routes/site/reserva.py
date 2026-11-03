from flask import Blueprint, abort, render_template, request

from frontend.web.constants import ASIENTOS_OCUPADOS_DEMO, FUNCIONES_DEMO, SERVICIOS_DEMO

reserva_bp = Blueprint('reserva', __name__)


def _render_reserva(funcion_id):
    funcion = next(
        (funcion for funcion in FUNCIONES_DEMO if funcion['id'] == funcion_id),
        FUNCIONES_DEMO[0],
    )
    return render_template(
        'site/reserva_butacas.html',
        funcion=funcion,
        asientos_ocupados=ASIENTOS_OCUPADOS_DEMO,
        servicios=SERVICIOS_DEMO,
    )


@reserva_bp.route('/<int:funcion_id>')
def butacas(funcion_id):
    return _render_reserva(funcion_id)


@reserva_bp.route('/butacas', methods=['GET', 'POST'])
def procesar():
    funcion_id = 101
    if request.method == 'POST':
        try:
            funcion_id = int(request.form.get('funcion_id', funcion_id))
        except ValueError:
            abort(400)

    return _render_reserva(funcion_id)
