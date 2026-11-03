from flask import Blueprint, render_template

login_bp = Blueprint('login', __name__)

@login_bp.route('/login')
def index():
    return render_template('site/login.html')