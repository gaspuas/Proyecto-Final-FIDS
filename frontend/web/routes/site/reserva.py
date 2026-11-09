import os
import requests
from flask import (
    Blueprint,
    abort,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
# Obtener URL del Backend desde el .env
API_URL = os.getenv('API_URL', 'http://127.0.0.1:5000')


reserva_bp = Blueprint('reserva', __name__)


def _obtener_funcion(funcion_id):
    """Consulta la función real a la API backend e incluye precio_base para Jinja2."""
    try:
        res = requests.get(f'{API_URL}/api/funciones/{funcion_id}', timeout=3)
        if res.status_code == 200:
            data = res.json()
            # Mapeamos precio_base por si el HTML lo requiere explícitamente
            precio = float(data.get('precio_entrada', data.get('precio_base', 4500.0)))
            data['precio_base'] = precio
            data['precio_entrada'] = precio
            return data
    except Exception as e:
        print(f"Error al consultar función {funcion_id} en el backend: {e}")

    precio_default = 4500.0
    return {
        'id': funcion_id,
        'pelicula': f'Película Función {funcion_id}',
        'fecha_hora': '19:30 hs',
        'capacidad_total': 50,
        'precio_base': precio_default,
        'precio_entrada': precio_default
    }

# Función helper para consultar butacas ocupadas desde la API
def _obtener_asientos_ocupados(funcion_id):
    try:
        res = requests.get(
            f'{API_URL}/api/funciones/{funcion_id}/butacas', timeout=3
        )
        if res.status_code == 200:
            data = res.json()
            # Retornamos la lista de códigos ocupados como strings
            return [str(b) for b in data.get('ocupadas', [])]
    except Exception as e:
        print(f'Error al consultar butacas ocupadas para función {funcion_id}: {e}')
    return []

# Función helper para consultar el catálogo de servicios de MySQL
def _obtener_servicios():
    try:
        res = requests.get(f'{API_URL}/api/servicios', timeout=3)
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        print(f'Error al consultar servicios en backend: {e}')

    # Retorno vacío o estructura por defecto si falla la API
    return []

# 1. PASO 1: Selección de Butacas
@reserva_bp.route('/butacas/<int:funcion_id>')
def butacas(funcion_id):
    funcion = _obtener_funcion(funcion_id)
    
    asientos_ocupados = _obtener_asientos_ocupados(funcion_id)

    return render_template(
        'site/reserva_butacas.html',
        funcion=funcion,
        asientos_ocupados=asientos_ocupados,
    )


# 2. PASO 2: Procesar Butacas -> Redirigir a Servicios (Candy Bar)
@reserva_bp.route('/butacas', methods=['GET', 'POST'])
def procesar():
    if request.method == 'POST':
        try:
            # Si no viene en el form, tomamos la función ID 1 en lugar de 101
            funcion_id = int(request.form.get('funcion_id', 1))
        except ValueError:
            abort(400)

        asientos = request.form.getlist('asientos')
        asientos_ocupados = _obtener_asientos_ocupados(funcion_id)
        if not asientos:
            funcion = _obtener_funcion(funcion_id)
            return render_template(
                'site/reserva_butacas.html',
                funcion=funcion,
                asientos_ocupados=asientos_ocupados,
                error='Debes seleccionar al menos una butaca.',
            )

        # Guardamos la selección temporal con el funcion_id real
        session['reserva_temp'] = {
            'funcion_id': funcion_id,
            'asientos': asientos,
        }

        # Redirigimos a la pantalla de Servicios
        return redirect(url_for('web.site.reserva.servicios'))

    # Si entran por GET directo a /butacas sin ID, redirigimos a la función 1
    return redirect(url_for('web.site.reserva.butacas', funcion_id=1))


# 3. PASO 3: Selección de Servicios / Combos
# 3. PASO 3: Selección de Servicios / Combos
@reserva_bp.route('/servicios', methods=['GET', 'POST'])
def servicios():
    reserva_temp = session.get('reserva_temp')
    if not reserva_temp:
        # Cambiado 101 por 1 para evitar IDs inexistentes en MySQL
        return redirect(url_for('web.site.reserva.butacas', funcion_id=1))

    # Obtenemos el funcion_id guardado previamente en el paso de Butacas
    funcion_id = reserva_temp.get('funcion_id', 1)
    funcion = _obtener_funcion(funcion_id)
    asientos = reserva_temp.get('asientos', [])
    
    servicios_catalogo = _obtener_servicios()
    # Dentro de la ruta de servicios o confirmación:
    precio_unitario = float(funcion.get('precio_base', funcion.get('precio_entrada', 4500.0)))

    compra = {
        'pelicula': funcion.get('pelicula', 'Película Seleccionada'),
        'funcion': funcion,
        'asientos': asientos,
        'butacas': asientos,
        'cantidad_asientos': len(asientos),
        'precio_base': precio_unitario,      # <--- AGREGADO PARA JINJA2
        'precio_unitario': precio_unitario,
        'total': len(asientos) * precio_unitario
    }

    if request.method == 'POST':
        servicios_ids = request.form.getlist('servicios')
        reserva_temp['servicios'] = servicios_ids
        session['reserva_temp'] = reserva_temp

        if not session.get('usuario') and not session.get('token'):
            return redirect(
                url_for(
                    'web.site.login.index',
                    next=url_for('web.site.reserva.confirmacion'),
                )
            )

        return redirect(url_for('web.site.reserva.confirmacion'))

    precio_entrada = 4500.0
    total_entradas_precio = len(asientos) * precio_entrada

    return render_template(
        'site/servicios.html',
        compra=compra,
        funcion=funcion,
        asientos=asientos,
        servicios=servicios_catalogo,
        total_entradas=total_entradas_precio,
        cantidad_maxima=len(asientos),
    )


# 4. PASO 4: Confirmación Final con QR
@reserva_bp.route('/confirmacion')
def confirmacion():
    reserva_temp = session.get('reserva_temp')
    usuario = session.get('usuario')

    if not reserva_temp or not usuario:
        return redirect(url_for('web.site.inicio.index'))

    asientos_lista = reserva_temp.get('asientos', [])
    servicios_elegidos = reserva_temp.get('servicios', [])
    # Cambiamos el fallback de 101 al ID 1 (existente en MySQL)
    funcion_id = reserva_temp.get('funcion_id', 1)

    payload = {
        'usuario_id': usuario.get('id', 1),
        'asientos': asientos_lista,
        'servicios': servicios_elegidos,
    }

    try:
        url_backend = f'{API_URL}/api/funciones/{funcion_id}/reservar'
        response = requests.post(
            url_backend,
            json=payload,
            headers={'Authorization': f"Bearer {session.get('token')}"},
            timeout=5,
        )

        if response.status_code in (200, 201):
            compra_data = response.json()
            session.pop('reserva_temp', None)

            return render_template(
                'site/confirmacion.html',
                compra=compra_data['compra'],
                total_entradas=compra_data['total_entradas'],
                elegidos=compra_data['elegidos'],
                total=compra_data['total'],
            )
        else:
            print(
                f'Error backend MySQL ({response.status_code}): {response.text}'
            )

    except Exception as e:
        print(f'Excepción al conectar con la API: {e}')

    # Fallback local con ID válido
    funcion = _obtener_funcion(funcion_id)
    precio_entrada = 4500.0
    total_entradas = len(asientos_lista) * precio_entrada
    total_servicios = sum(
        float(s.get('precio', 0)) * int(s.get('cantidad', 1))
        for s in servicios_elegidos
    )

    compra_fallback = {
        'codigo': 'RES-883921',
        'pelicula': funcion.get('pelicula', 'Película Seleccionada'),
        'fecha_hora': f"{funcion.get('fecha', 'Hoy')} {funcion.get('fecha_hora', '19:30 hs')}",
        'butacas': asientos_lista,
    }

    session.pop('reserva_temp', None)

    return render_template(
        'site/confirmacion.html',
        compra=compra_fallback,
        total_entradas=total_entradas,
        elegidos=servicios_elegidos,
        total=total_entradas + total_servicios,
    )