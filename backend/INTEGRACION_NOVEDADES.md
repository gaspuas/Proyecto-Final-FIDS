# Integración segura del módulo de novedades — Cine Paradiso

Este ZIP es un **parche de integración**, no un repositorio completo. Fue adaptado a
partir de `backend-novedades.zip` y comparado con el ZIP previo del proyecto.
**No sobrescribas `backend/src/routes/__init__.py`, `db_connection.py` ni `requirements.txt`.**
El repositorio `main` pudo haber cambiado después del ZIP que recibimos.

## Qué archivos copiar

Copiar `backend/src/routes/novedades.py`, `backend/src/services/novedades_services.py`,
`backend/src/repositories/novedades_repository.py`, `backend/src/validators/novedades_validators.py`
y `backend/src/utils/novedades_auth.py` a las rutas equivalentes del proyecto.
Copiar `database/migrations/001_novedades.sql`. No es necesario copiar nada del
viejo `backend/db/` ni la antigua aplicación Flask aislada.

## Un único cambio manual en backend/src/routes/__init__.py existente

Agregar import (con los demás imports):

```python
from backend.src.routes.novedades import novedades_bp
```

Agregar registro (junto a los demás `app.register_blueprint(...)`):

```python
app.register_blueprint(novedades_bp)
```

NO reemplazar el resto de `backend/src/routes/__init__.py`: conservar auth, compras, servicios, etc.
Si ya existe un registro para `/api/novedades`, no duplicarlo.

## Conexión a la misma MySQL del grupo

El repository usa `backend.src.utils.db_connection.get_db_connection()` y requiere
el conector `mysql-connector-python` (ya declarado en los requirements del proyecto original).
Esta función debe devolver una conexión normal `mysql.connector`; los cursores deben
aceptar `conn.cursor(dictionary=True)`. No usa PyMySQL ni crea una segunda base.
Valores de `.env` deben corresponder con tu Docker (`DB_NAME=cine_paradiso_db`, `DB_PORT=3307`
en el entorno de ejemplo). Verificá que `db_connection.py` **realmente lea** el `.env`.

## Crear tabla SIN perder los datos

Desde la carpeta principal, con el contenedor MySQL levantado:

```bash
sudo docker exec -i cine_paradiso_db mysql -u cineAdmin -p cine_paradiso_db < database/migrations/001_novedades.sql
```

Si tu contenedor o usuario tiene otro nombre, ajustalos. Pedirá contraseña
al iniciar la sesión interactiva de MySQL.
**No uses `docker compose down -v`**, porque eliminaría el volumen.

No se insertan promociones ficticias automáticamente. Para probar el carrusel,
cargar novedades reales con URLs de imágenes accesibles desde el navegador.
El frontend renderiza el campo `imagen_url` literalmente: `/static/img/...` debe
existir en el servidor frontend; una ruta de Linux `/home/...` no es URL pública.

## Endpoints

- `GET /api/novedades`: público. Responde `[]` si no hay novedades vigentes.
- `GET /api/novedades/admin/todas`: listado administrativo.
- `POST /api/novedades`: crear (JSON).
- `PUT /api/novedades/<id>`: editar (JSON).
- `DELETE /api/novedades/<id>`: eliminar.

El JSON de listado público es un arreglo de objetos con exactamente:
`id`, `titulo`, `descripcion`, `imagen_url`, `tipo`, `enlace`, `orden`.
Una novedad se muestra cuando `activo=1` y las fechas abarcan la fecha actual.
Solo se admiten tipos `estreno`, `oferta`, `publicidad`.

## Seguridad administrativa — IMPORTANTE

Los endpoints administrativos quedan **cerrados por defecto** (503 si no hay
configuración de autorización). NO existe el token inseguro `cambiar-este-token`.
Para pruebas de integración podés crear en el **servidor backend** la variable de
entorno `NOVEDADES_ADMIN_TOKEN` con un secreto aleatorio de 32+ caracteres y enviar
la cabecera `X-Admin-Token`. El token no debe guardarse en Git, HTML ni JavaScript.

**Para el proyecto final:** conectar la autorización real por rol administrador
implementando una función verificadora sobre el sistema actual del grupo y asignarla:

```python
app.config["NOVEDADES_ADMIN_AUTHORIZER"] = verificar_admin_actual
```

La función `verificar_admin_actual()` **debe verificar el usuario autenticado en el
servidor** y retornar `True` solo si su rol es administrador. No confiar en un rol
enviado por el cliente. La función y la integración con sesiones/tokens reales NO
pueden implementarse con seguridad sin revisar la autenticación vigente del `main`.

## Pruebas de integración

1. Levantar MySQL y aplicar migración.
2. Levantar backend puerto 5001 (ej. `python -m flask --app backend.app run --port 5001`).
3. `curl -i http://127.0.0.1:5001/api/novedades` debe devolver HTTP 200 y `[]` o un JSON de novedades.
4. Verificar `BACKEND_URL=http://127.0.0.1:5001` en frontend y que se lea `.env`.
5. Abrir frontend en 5000: al haber contenido válido, se muestra el carrusel.
6. Verificar que un anónimo no pueda POST/PUT/DELETE; deben retornar 403 o 503.
7. Probar datos inválidos, orden, fechas, URL local existente y rotación de slides.

## Limitaciones comprobadas

- No se recibió el `main` **actual**; se comparó con un ZIP anterior y trazas de Git.
- Los tests offline comprueban validaciones, acceso a datos simulado y estructura.
- El funcionamiento completo requiere MySQL, Flask y el código reciente del grupo.
