"""Autorización de novedades mediante TokenSession y rol actual en MySQL."""
from backend.src.utils.token_auth import admin_token_required

# Se conserva el nombre usado por backend/src/routes/novedades.py.
admin_novedades_required = admin_token_required
