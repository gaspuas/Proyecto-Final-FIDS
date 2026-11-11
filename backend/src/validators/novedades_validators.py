"""Validaciones para la API de novedades."""
from datetime import datetime
from urllib.parse import urlsplit

TIPOS_VALIDOS = {"estreno", "oferta", "publicidad"}
LIMITES = {"titulo": 150, "imagen_url": 500, "enlace": 500}
CAMPOS = {"titulo", "descripcion", "imagen_url", "tipo", "enlace", "orden",
          "fecha_inicio", "fecha_fin", "activo"}


def _url_valida(url):
    if not isinstance(url, str) or not url.strip():
        return False
    url = url.strip()
    if url.startswith("/"):
        return not url.startswith("//") and not any(c in url for c in "\r\n\\")
    parts = urlsplit(url)
    return parts.scheme in {"http", "https"} and bool(parts.netloc) and not any(c in url for c in "\r\n")


def validar_novedad(data, parcial=False):
    if not isinstance(data, dict):
        return {}, ["El cuerpo debe ser un objeto JSON"]
    errores, limpio = [], {}
    extras = set(data) - CAMPOS
    if extras:
        errores.append("Campos desconocidos: " + ", ".join(sorted(extras)))

    if not parcial:
        for key in ("titulo", "imagen_url", "tipo"):
            if not data.get(key):
                errores.append(f"'{key}' es obligatorio")
    if parcial and not data:
        errores.append("Se necesita al menos un campo para actualizar")

    for key in ("titulo", "descripcion", "imagen_url", "enlace"):
        if key not in data:
            continue
        valor = data[key]
        if valor is None and key in ("descripcion", "enlace"):
            limpio[key] = None
        elif not isinstance(valor, str):
            errores.append(f"'{key}' debe ser texto")
        elif (key in ("titulo", "imagen_url") and not valor.strip()):
            errores.append(f"'{key}' no puede estar vacío")
        elif len(valor) > LIMITES.get(key, 10000):
            errores.append(f"'{key}' es demasiado largo")
        elif key in ("imagen_url", "enlace") and valor and not _url_valida(valor):
            errores.append(f"'{key}' debe ser una URL http(s) o ruta local /...")
        else:
            limpio[key] = valor.strip() if key != "descripcion" else valor

    if "tipo" in data:
        if not isinstance(data["tipo"], str) or data["tipo"] not in TIPOS_VALIDOS:
            errores.append("'tipo' debe ser estreno, oferta o publicidad")
        else:
            limpio["tipo"] = data["tipo"]

    if "orden" in data:
        if type(data["orden"]) is not int or data["orden"] < 0:
            errores.append("'orden' debe ser entero no negativo")
        else:
            limpio["orden"] = data["orden"]
    if "activo" in data:
        if type(data["activo"]) is not bool:
            errores.append("'activo' debe ser true/false")
        else:
            limpio["activo"] = int(data["activo"])

    for key in ("fecha_inicio", "fecha_fin"):
        if key not in data:
            continue
        valor = data[key]
        if valor is None:
            limpio[key] = None
        elif not isinstance(valor, str):
            errores.append(f"'{key}' debe ser texto de fecha o null")
        else:
            try:
                limpio[key] = datetime.fromisoformat(valor.strip()).strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                errores.append(f"'{key}' debe ser una fecha ISO válida")

    inicio = limpio.get("fecha_inicio")
    fin = limpio.get("fecha_fin")
    if inicio is not None and fin is not None and inicio > fin:
        errores.append("fecha_fin debe ser posterior o igual a fecha_inicio")
    return limpio, errores
