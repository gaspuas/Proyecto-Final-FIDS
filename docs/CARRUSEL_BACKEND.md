# Contrato pendiente del backend: carrusel de novedades

Este frontend **ya consulta** `GET {BACKEND_URL}/api/novedades` con Python `requests` desde `web/services/novedades.py`. No utiliza `fetch` ni llamadas desde JS al servidor. Mientras el backend no esté listo, la página funciona y muestra un estado sin novedades.

## Para el compañero de backend / base de datos

1. Crear la tabla `novedades` en MySQL (ejemplo de campos propuestos: `id`, `titulo`, `descripcion`, `imagen_url`, `tipo`, `enlace`, `orden`, `fecha_inicio DATETIME`, `fecha_fin DATETIME`, `activo`). Estas columnas **no existen** en el schema original. Acordar esquema final antes de escribir consultas.
2. Implementar `GET /api/novedades` en Flask, con respuesta JSON (lista directamente o `{"novedades": [...]}`). Debe devolver solo las novedades activas, vigentes según fecha y ordenadas por `orden`. No incluir datos de ejemplo en el código.
3. Campos mínimos de cada objeto: `titulo` (texto) e `imagen_url` (URL). Opcionales: `id`, `descripcion`, `tipo`, `enlace`, `orden`.
4. Proteger endpoints administrativos de alta/edición/baja de novedades. El GET público debe ser accesible para la home y respetar el requisito de seguridad correspondiente.
5. Establecer `BACKEND_URL` en el entorno del proceso frontend, por ejemplo `http://127.0.0.1:5001`. **Es una URL de ejemplo**: debe coincidir con el puerto real del backend. El frontend usa por defecto ese valor, y ya ocupa 5000 según `app.py`: arrancar dos apps en el mismo puerto da conflicto.
6. Para administrar el contenido posteriormente, implementar los endpoints CRUD correspondientes en el backend y pantallas en backoffice.

## Pendiente de integración

- La implementación del endpoint, las tablas y el panel de administración son tareas del backend/backoffice: **no se modificaron** en esta entrega.
- No se insertaron ofertas, anuncios ni películas de prueba. El carrusel se llenará automáticamente al recibir novedades reales.
- JavaScript (`static/js/main.js`) solo rota slides ya renderizados por Jinja, sin hacer peticiones HTTP.
- El contenido existente de `inicio.html` se mantiene bajo el carrusel para que pueda recorrerse con scroll.
