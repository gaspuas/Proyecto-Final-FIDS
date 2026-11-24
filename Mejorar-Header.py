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
    print('El nuevo header ya está aplicado. No se cambió la plantilla.')
    new_base = old
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
                    <span class="nav__saludo" title="Cuenta actual">Hola, {{ session['usuario']['nombre'] }}</span>
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
/* Solo barra superior. No modifica el carrusel ni el panel admin. */
.header-principal .nav {
    width: 100%;
    max-width: 1800px;
    margin-inline: auto;
    min-height: 82px;
    padding: 0.9rem clamp(1.1rem, 3.6vw, 4.25rem);
    display: flex;
    align-items: center;
    justify-content: space-between;
    column-gap: clamp(2rem, 5vw, 6rem);
    row-gap: 0.75rem;
}
.header-principal .navbar__brand {
    display: flex;
    align-items: center;
    flex: 0 0 auto;
    white-space: nowrap;
}
.header-principal .navbar__brand-name {
    font-size: clamp(1.45rem, 1.9vw, 1.9rem);
    letter-spacing: 0.025em;
}
.header-principal .nav__menu {
    min-width: 0;
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: clamp(1rem, 2.5vw, 3rem);
}
.header-principal .nav__links-principales,
.header-principal .nav__cuenta {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.4rem clamp(0.3rem, 0.9vw, 1rem);
}
.header-principal .nav__cuenta { justify-content: flex-end; }
.header-principal .navbar__link {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    white-space: nowrap;
    border-radius: 10px;
    padding: 0.65rem clamp(0.55rem, 0.9vw, 1rem);
    line-height: 1.25;
}
.header-principal .nav__saludo {
    color: var(--color-texto, #f0f0f3);
    font-size: 0.88rem;
    font-weight: 600;
    white-space: nowrap;
    margin-right: 0.3rem;
    padding: 0.55rem 0.65rem;
    border-left: 1px solid var(--color-borde, rgba(212,175,55,.25));
}
.header-principal .nav__cuenta form {
    display: flex;
    align-items: center;
    margin: 0;
}
.header-principal .nav__cuenta button.nav__salir {
    appearance: none;
    -webkit-appearance: none;
    font: inherit;
    font-size: 0.9rem;
    font-weight: 600;
    color: var(--color-dorado, #d4af37);
    background: rgba(212,175,55,.09);
    border: 1px solid rgba(212,175,55,.35);
    border-radius: 10px;
    cursor: pointer;
    transition: background .2s ease, border-color .2s ease;
}
.header-principal .nav__cuenta button.nav__salir:hover,
.header-principal .nav__cuenta button.nav__salir:focus-visible {
    color: var(--color-dorado-hover, #e5b938);
    background: rgba(212,175,55,.18);
    border-color: var(--color-dorado, #d4af37);
}
.header-principal .nav__ingresar {
    border: 1px solid var(--color-borde, rgba(212,175,55,.25));
    color: var(--color-dorado, #d4af37);
}
@media (max-width: 1060px) {
    .header-principal .nav { flex-wrap: wrap; justify-content: center; gap: 0.8rem 1.8rem; }
    .header-principal .nav__menu { flex: 1 1 100%; justify-content: center; flex-wrap: wrap; gap: 0.5rem 1.8rem; }
    .header-principal .nav__links-principales,
    .header-principal .nav__cuenta { justify-content: center; }
}
@media (max-width: 600px) {
    .header-principal .nav { flex-direction: column; padding: 0.75rem 1rem; gap: 0.55rem; }
    .header-principal .nav__menu { gap: 0.3rem 0.8rem; }
    .header-principal .navbar__link { padding: 0.55rem 0.65rem; font-size: 0.86rem; }
    .header-principal .nav__saludo { width: 100%; text-align: center; border-left: 0; padding: 0.25rem; }
    .header-principal .nav__cuenta { row-gap: 0.25rem; }
}
/* FIN HEADER DISTRIBUIDO */
'''
new_css = css if mark in css else css + patch
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
