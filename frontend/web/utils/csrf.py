"""Tokens CSRF para formularios que modifican estado a través de cookies."""
from secrets import compare_digest, token_urlsafe

from flask import abort, request, session


def csrf_token_form():
    if 'csrf_token_global' not in session:
        session['csrf_token_global'] = token_urlsafe(32)
    return session['csrf_token_global']


def requerir_csrf():
    enviado = request.form.get('csrf_token', '')
    esperado = session.get('csrf_token_global', '')
    if not enviado or not esperado or not compare_digest(enviado, esperado):
        abort(400, 'El formulario venció o no es válido. Recargá la página.')
