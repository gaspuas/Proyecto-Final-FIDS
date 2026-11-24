# -*- coding: utf-8 -*-
# Mejora solamente la barra superior.
from pathlib import Path
from datetime import datetime
import shutil

root = Path(__file__).resolve().parent
base = root / 'frontend/templates/base.html'
css_path = root / 'frontend/static/css/estilos.css'
if not base.is_file() or not css_path.is_file():
    raise SystemExit('ERROR: Guardá este archivo en la carpeta principal Proyecto-Final-FIDS.')

old = base.read_text(encoding='utf-8')
start_mark = '            {% block navbar_menu %}'
end_mark = '            {% endblock %}'
start = old.find(start_mark)
end = old.find(end_mark, start)
if start == -1 or end == -1:
    raise SystemExit('ERROR: No se reconoce la navegación original. No se cambió ningún archivo.')
end += len(end_mark)
original_section = old[start:end]
if 'nav__links-principales' in original_section:
    greeting_old = "<span class=\"nav__saludo\" title=\"Cuenta actual\">Hola, {{ session['usuario']['nombre'] }}</span>"
    greeting_new = """<span class=\"nav__saludo\" title=\"Sesión iniciada\">
                        <span class=\"nav__avatar\" aria-hidden=\"true\">{{ session['usuario']['nombre'][:1]|upper }}</span>
                        <span class=\"nav__saludo-texto\"><small>Bienvenido</small><strong>Hola, {{ session['usuario']['nombre'] }}</strong></span>
                    </span>"""
    new_section = original_section.replace(greeting_old, greeting_new)
    new_base = old[:start] + new_section + old[end:]
else:
    checks = ('web.site.home.index', 'web.site.peliculas.index', 'web.site.login.logout', 'web.admin.index', 'web.site.compra.historial', 'session.get(\'usuario\')')
    if not all(c in original_section for c in checks):
        raise SystemExit('ERROR: La navegación actual es distinta. No se cambió ningún archivo.')
    section = '''            {% block navbar_menu %}
            <nav class="nav__menu" aria-label="Navegación principal">
                <div class="nav__links-principales">
                    <a href="{{ url_for('web.site.home.index') }}"
                       class="navbar__link {% if request.endpoint == 'web.site.home.index' %}navbar__link--active{% endif %}">Inicio</a>
                    <a href="{{ url_for('web.site.peliculas.index') }}"
                       class="navbar__link {% if request.endpoint and request.endpoint.startswith('web.site.peliculas') %}navbar__link--active{% endif %}">Cartelera</a>
                    {% if session.get('usuario') and session['usuario'].get('rol') == 'administrador' %}
                    <a class="navbar__link {% if request.endpoint and request.endpoint.startswith('web.admin') %}navbar__link--active{% endif %}"
                       href="{{ url_for('web.admin.index') }}">Administración</a>
                    {% endif %}
                </div>
                <div class="nav__cuenta">
                    {% if session.get('usuario') %}
                    <span class="nav__saludo" title="Sesión iniciada">
                        <span class="nav__avatar" aria-hidden="true">{{ session['usuario']['nombre'][:1]|upper }}</span>
                        <span class="nav__saludo-texto"><small>Bienvenido</small><strong>Hola, {{ session['usuario']['nombre'] }}</strong></span>
                    </span>
                    <a class="navbar__link {% if request.endpoint and request.endpoint.startswith('web.site.compra') %}navbar__link--active{% endif %}"
                       href="{{ url_for('web.site.compra.historial') }}">Mis compras</a>
                    <form action="{{ url_for('web.site.login.logout') }}" method="POST">
                        <button class="navbar__link nav__salir" type="submit">Cerrar sesión</button>
                    </form>
                    {% else %}
                    <a href="{{ url_for('web.site.login.index') }}"
                       class="navbar__link nav__ingresar {% if request.endpoint and request.endpoint.startswith('web.site.login') %}navbar__link--active{% endif %}">Ingresar</a>
                    {% endif %}
                </div>
            </nav>
            {% endblock %}'''
    new_base = old[:start] + section + old[end:]

css = css_path.read_text(encoding='utf-8')
mark = '/* HEADER DISTRIBUIDO - CINE PARADISO */'
patch = r'''

/* HEADER DISTRIBUIDO - CINE PARADISO */
/* La marca y navegacion quedan juntas, la cuenta a la derecha. */
.header-principal .nav {
    box-sizing: border-box;
    width: 100%;
    max-width: 1900px;
    margin-inline: auto;
    min-height: 80px;
    padding: 0.85rem clamp(1rem, 3vw, 3.5rem);
    display: flex;
    align-items: center;
    justify-content: flex-start;
    gap: clamp(1.5rem, 3vw, 3.5rem);
}
.header-principal .navbar__brand {
    display: inline-flex;
    align-items: center;
    flex: none;
    white-space: nowrap;
}
.header-principal .navbar__brand-name {
    font-size: clamp(1.4rem, 1.8vw, 1.85rem);
    letter-spacing: .035em;
}
.header-principal .nav__menu {
    flex: 1 1 auto;
    min-width: 0;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
}
.header-principal .nav__links-principales,
.header-principal .nav__cuenta {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: .35rem;
}
.header-principal .nav__links-principales { justify-content: flex-start; }
.header-principal .nav__cuenta { margin-left: auto; justify-content: flex-end; }
.header-principal .navbar__link {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    white-space: nowrap;
    border-radius: 10px;
    padding: .65rem clamp(.55rem, .8vw, .95rem);
    line-height: 1.25;
}
/* Saludo con avatar, sin comportamiento de boton */
.header-principal .nav__saludo {
    display: inline-flex;
    align-items: center;
    gap: .6rem;
    padding: .35rem .9rem .35rem .45rem;
    margin-right: .35rem;
    background: rgba(212,175,55,.065);
    border: 1px solid rgba(212,175,55,.22);
    border-radius: 999px;
    color: #f7f2e8;
    max-width: 270px;
}
.header-principal .nav__avatar {
    width: 34px;
    height: 34px;
    flex: 0 0 34px;
    display: inline-grid;
    place-items: center;
    border-radius: 50%;
    background: linear-gradient(135deg, #e6c76a, #a77b24);
    color: #20180b;
    font-size: .9rem;
    font-weight: 800;
}
.header-principal .nav__saludo-texto {
    display: flex;
    flex-direction: column;
    line-height: 1.2;
    min-width: 0;
}
.header-principal .nav__saludo-texto small {
    font-size: .64rem;
    letter-spacing: .08em;
    text-transform: uppercase;
    color: #d8ba72;
    font-weight: 600;
}
.header-principal .nav__saludo-texto strong {
    font-size: .83rem;
    font-weight: 600;
    white-space: nowrap;
    text-overflow: ellipsis;
    overflow: hidden;
}
.header-principal .nav__cuenta form { margin: 0; padding: 0; display: flex; align-items: center; }
.header-principal .nav__cuenta button.nav__salir {
    appearance: none;
    -webkit-appearance: none;
    font: inherit;
    font-size: .9rem;
    font-weight: 600;
    color: #d4af37;
    background: rgba(212,175,55,.09);
    border: 1px solid rgba(212,175,55,.35);
    border-radius: 10px;
    cursor: pointer;
}
.header-principal .nav__cuenta button.nav__salir:hover,
.header-principal .nav__cuenta button.nav__salir:focus-visible {
    color: #eacb77;
    background: rgba(212,175,55,.18);
    border-color: #d4af37;
}
.header-principal .nav__ingresar { border: 1px solid rgba(212,175,55,.3); color: #d4af37; }
@media (max-width: 1100px) {
    .header-principal .nav { flex-wrap: wrap; gap: .65rem 1.5rem; }
    .header-principal .nav__menu { flex: 1 1 100%; }
    .header-principal .nav__cuenta { margin-left: auto; }
}
@media (max-width: 650px) {
    .header-principal .nav { flex-direction: column; padding: .7rem .8rem; gap: .45rem; }
    .header-principal .nav__menu { flex-wrap: wrap; justify-content: center; gap: .5rem; }
    .header-principal .nav__links-principales,
    .header-principal .nav__cuenta { justify-content: center; width: 100%; margin-left: 0; }
    .header-principal .navbar__link { padding: .5rem .65rem; font-size: .86rem; }
    .header-principal .nav__saludo { margin-right: 0; }
}
/* FIN HEADER DISTRIBUIDO */
'''
end_marker = '/* FIN HEADER DISTRIBUIDO */'
if mark in css and end_marker in css:
    old_start = css.index(mark)
    old_end = css.index(end_marker, old_start) + len(end_marker)
    new_css = css[:old_start] + patch.strip() + css[old_end:]
else:
    new_css = css + patch
if new_base == old and new_css == css:
    print('Ya está todo aplicado. No se modificaron archivos.')
    raise SystemExit(0)
# Backup first; never overwrite previous backups.
stamp = datetime.now().strftime('%Y%m%d-%H%M%S')
for path, previous, revised in ((base, old, new_base), (css_path, css, new_css)):
    if previous != revised:
        backup = path.with_name(path.name + '.bak-header-' + stamp)
        shutil.copy2(path, backup)
        path.write_text(revised, encoding='utf-8')
        print(f'Actualizado: {path.relative_to(root)}')
        print(f'Respaldo: {backup.name}')
print('Listo. El carrusel, admin, novedades y JS no se modificaron.')
