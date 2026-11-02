import datetime

def validar_query_params_cartelera(sede_id, fecha):
    if sede_id is not None:
        try:
            int(sede_id)
        except ValueError:
            return False, "El parámetro 'sede_id' debe ser un número entero válido."
            
    if fecha is not None:
        try:
            # Valida el formato de fecha (YYYY-MM-DD)
            datetime.datetime.strptime(fecha, '%Y-%m-%d')
        except ValueError:
            return False, "El parámetro 'fecha' debe tener el formato YYYY-MM-DD válido."
            
    return True, None

def validar_id_pelicula(pelicula_id):
    if not pelicula_id:
        return False, "El ID de la película es obligatorio."
    try:
        # Validación de tipo fuerte 
        int(pelicula_id)
        if int(pelicula_id) <= 0:
            return False, "El ID de la película debe ser un número entero positivo."
        return True, None
    except ValueError:
        return False, "El ID de la película debe ser un número entero válido."