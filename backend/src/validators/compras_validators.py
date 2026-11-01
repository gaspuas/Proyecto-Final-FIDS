
def validar_id_recurso(recurso_id: int) -> tuple[bool, str | None]:
    if not isinstance(recurso_id, int) or recurso_id <= 0:
        return False, "El identificador del recurso debe ser un entero positivo"
    return True, None


def validar_body_crear_compra(data: dict) -> tuple[dict, str | None]:
    if not data or not isinstance(data, dict):
        return {}, "Debe enviar un objeto JSON válido."

    campos_permitidos = {'id_usuario', 'id_funcion', 'butacas', 'servicios'}
    campos_enviados = set(data.keys())
    desconocidos = campos_enviados - campos_permitidos
    if desconocidos:
        return {}, (
            "Los siguientes campos no estan permitidos: "
            + ", ".join(sorted(desconocidos)) + "."
        )

    id_usuario = data.get('id_usuario')
    id_funcion = data.get('id_funcion')
    butacas = data.get('butacas')
    servicios = data.get('servicios', [])

    if not isinstance(id_usuario, int) or isinstance(id_usuario, bool) or id_usuario <= 0:
        return {}, "El campo 'id_usuario' es obligatorio y debe ser un entero positivo."

    if not isinstance(id_funcion, int) or isinstance(id_funcion, bool) or id_funcion <= 0:
        return {}, "El campo 'id_funcion' es obligatorio y debe ser un entero positivo."

    if not isinstance(butacas, list) or not butacas:
        return {}, "El campo 'butacas' debe contener al menos una butaca."

    butacas_limpias = []
    for butaca in butacas:
        if isinstance(butaca, bool) or not isinstance(butaca, (int, str)):
            return {}, "Cada butaca debe ser un número entero positivo."
        butaca_str = str(butaca).strip()
        if not butaca_str.isdigit() or int(butaca_str) <= 0:
            return {}, "Cada butaca debe identificarse con un número entero positivo."
        if len(butaca_str) > 3:
            return {}, "El numero de butaca no puede superar los 3 caracteres."
        butacas_limpias.append(butaca_str)

    if len(set(butacas_limpias)) != len(butacas_limpias):
        return {}, "No se permite seleccionar más de una vez la misma butaca."

    if servicios is None:
        servicios = []
    if not isinstance(servicios, list):
        return {}, "El campo 'servicios' debe ser una lista."

    servicios_limpios = []
    ids_servicios = set()

    for indice, servicio in enumerate(servicios, start=1):
        if not isinstance(servicio, dict):
            return {}, f"El servicio #{indice} debe ser un JSON."

        campos_servicio = set(servicio.keys())
        if campos_servicio != {'id', 'cant'}:
            return {}, f"El servicio #{indice} debe contener únicamente los campos 'id' y 'cant'"

        id_servicio = servicio.get('id')
        cantidad = servicio.get('cant')

        if not isinstance(id_servicio, int) or isinstance(id_servicio, bool) or id_servicio <= 0:
            return {}, f"El ID del servicio #{indice} debe ser un entero positivo."

        if not isinstance(cantidad, int) or isinstance(cantidad, bool) or cantidad <= 0:
            return {}, f"La cantidad del servicio #{indice} debe ser un entero positivo."

        if id_servicio in ids_servicios:
            return {}, "No se permite repetir un servicio. Enviá una sola entrada con la cantidad total."

        ids_servicios.add(id_servicio)
        servicios_limpios.append({'id': id_servicio, 'cant': cantidad})

    return {
        'id_usuario': id_usuario,
        'id_funcion': id_funcion,
        'butacas': butacas_limpias,
        'servicios': servicios_limpios
    }, None
