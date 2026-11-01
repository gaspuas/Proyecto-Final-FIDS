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