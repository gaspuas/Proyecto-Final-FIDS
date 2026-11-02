from flask import Flask, render_template, request, url_for as flask_url_for
app = Flask(__name__)

# Configuración global simulada para Jinja2
app.config['config'] = {
    'web.site.peliculas.index': True,
    'web.site.peliculas.detalle': True,
    'web.site.reserva.butacas': True,
    'web.site.reserva.procesar': True
}

# Inyectar 'config' en el contexto global de Jinja2
@app.context_processor
def inject_config():
    return dict(config=app.config['config'])

# Helper centralizado para url_for en entorno local
@app.context_processor
def inject_url_for_helpers():
    def custom_url_for(endpoint, **values):
        if endpoint == 'static':
            return flask_url_for('static', **values)
        
        if 'pelicula_id' in values or endpoint == 'web.site.peliculas.detalle':
            pelicula_id = values.get('pelicula_id', 1)
            return f"/pelicula/{pelicula_id}"
            
        if 'funcion_id' in values or endpoint == 'web.site.reserva.butacas':
            # Apuntamos a /reserva/butacas para procesar por POST
            return "/reserva/butacas"

        if endpoint == 'web.site.home.index':
            return "/"
        if endpoint in ['web.site.peliculas.index', 'cartelera']:
            return "/cartelera"
        if endpoint == 'web.site.login.index':
            return "/login"
            
        return "/"

    return dict(url_for=custom_url_for)

# MOCK DATA
PELICULAS_DEMO = [
    {
        'id': 1,
        'titulo': 'Cinema Paradiso',
        'genero': 'Drama / Clásico',
        'duracion_minutos': 155,
        'clasificacion': 'ATP',
        'es_reestreno': True,
        'director': 'Giuseppe Tornatore',
        'sinopsis': 'Un cineasta recuerda su infancia y su entrañable amistad con el proyeccionista del cine de su pequeño pueblo italiano.',
        'poster_url': 'https://image.tmdb.org/t/p/w500/8kOWDBK6XlPUzcku9wGbd2UOf66.jpg'
    },
    {
        'id': 2,
        'titulo': 'Interstellar',
        'genero': 'Ciencia Ficción',
        'duracion_minutos': 169,
        'clasificacion': '+13',
        'es_reestreno': False,
        'director': 'Christopher Nolan',
        'sinopsis': 'Un equipo de exploradores viaja a través de un agujero de gusano para garantizar la supervivencia de la humanidad.',
        'poster_url': 'https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBv9B.jpg'
    }
]

FUNCIONES_DEMO = [
    {'id': 101, 'nombre_local': 'Paradiso Central', 'numero_sala': 1, 'fecha_hora': '05/11/2026 20:00', 'precio_base': 4500.00, 'filas': 5, 'columnas': 6},
    {'id': 102, 'nombre_local': 'Paradiso Norte', 'numero_sala': 3, 'fecha_hora': '05/11/2026 22:30', 'precio_base': 4800.00, 'filas': 5, 'columnas': 6}
]

SERVICIOS_DEMO = [
    {'id': 1, 'nombre': 'Combo Pochoclo + Gaseosa', 'descripcion': 'Balde de pochoclos grandes y 2 gaseosas medianas.', 'precio': 3500.00},
    {'id': 2, 'nombre': 'Estacionamiento 3hs', 'descripcion': 'Pase de estacionamiento cubierto en la sucursal.', 'precio': 2000.00}
]

RESENAS_DEMO = [
    {'nombre_usuario': 'Martín G.', 'puntuacion': 5, 'comentario': 'Una joya del cine. Excelente calidad de imagen.'}
]

# RUTAS DE NAVEGACIÓN
@app.route('/')
def inicio():
    return render_template('site/inicio.html', peliculas=PELICULAS_DEMO)

@app.route('/cartelera')
def cartelera():
    return render_template('site/cartelera.html', peliculas=PELICULAS_DEMO)

@app.route('/pelicula/<int:pelicula_id>')
def detalle(pelicula_id):
    pelicula = next((p for p in PELICULAS_DEMO if p['id'] == pelicula_id), PELICULAS_DEMO[0])
    return render_template('site/pelicula_detalle.html', pelicula=pelicula, funciones=FUNCIONES_DEMO, resenas=RESENAS_DEMO)

@app.route('/reserva/<int:funcion_id>', methods=['GET'])
@app.route('/reserva/butacas', methods=['GET', 'POST'])
def reserva(funcion_id=101):
    if request.method == 'POST':
        funcion_id = int(request.form.get('funcion_id', 101))

    funcion = next((f for f in FUNCIONES_DEMO if f['id'] == funcion_id), FUNCIONES_DEMO[0])
    return render_template('site/reserva_butacas.html', funcion=funcion, asientos_ocupados=['F1-C2', 'F2-C3'], servicios=SERVICIOS_DEMO)

@app.route('/login')
def login():
    return "<div style='background:#121212;color:#fff;height:100vh;padding:40px;font-family:sans-serif;'><h2>Pantalla de Login (Próximamente)</h2><a href='/' style='color:#f39c12;'>← Volver al inicio</a></div>"

if __name__ == '__main__':
    app.run(debug=True, port=5000)