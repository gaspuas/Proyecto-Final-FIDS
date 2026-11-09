import os
from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

login_bp = Blueprint('login', __name__)


@login_bp.route('/login', methods=['GET', 'POST'])
def index():
    next_url = request.args.get('next') or request.form.get('next')

    if request.method == 'POST':
        action_type = request.form.get('action_type', 'login')
        email = request.form.get('email')
        password = request.form.get('password')

        if action_type == 'registro':
            nombre = request.form.get('nombre')
            session['usuario'] = {
                'id': 1,
                'nombre': nombre,
                'email': email,
            }
        else:
            session['usuario'] = {
                'id': 1,
                'nombre': 'Usuario Demo',
                'email': email,
            }

        session['token'] = 'token-demo-xyz123'

        # Si venía de la reserva, redirige a confirmación
        if next_url:
            return redirect(next_url)

        return redirect(url_for('web.site.inicio.index'))

    return render_template('site/login.html', next=next_url)