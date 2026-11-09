const formularioServicios = document.getElementById('form-servicios');

// Validamos que totalEntradas sea un número real, si da NaN usa 0
const totalEntradas = Number(formularioServicios.dataset.totalEntradas) || 0;
const cantidades = Array.from(formularioServicios.querySelectorAll('.servicios-lista__cantidad'));
const resumenServicios = document.getElementById('resumen-servicios');
const resumenTotal = document.getElementById('resumen-total');

function leerCantidad(campo) {
    const cantidad = Number.parseInt(campo.value, 10);
    if (Number.isNaN(cantidad)) {
        return 0;
    }
    // Si campo.max no viene o es NaN, no limitamos con Math.min a NaN
    const maximo = Number.parseInt(campo.max, 10);
    const valorValido = Math.max(cantidad, 0);

    return Number.isNaN(maximo) ? valorValido : Math.min(valorValido, maximo);
}

function actualizarResumen() {
    const totalServicios = cantidades.reduce(
        (total, campo) => total + leerCantidad(campo) * (Number(campo.dataset.precio) || 0),
        0,
    );
    if (resumenServicios) resumenServicios.textContent = totalServicios.toLocaleString('es-AR');
    if (resumenTotal) resumenTotal.textContent = (totalEntradas + totalServicios).toLocaleString('es-AR');
}

cantidades.forEach((campo) => {
    campo.addEventListener('input', actualizarResumen);

    // Al salir del campo se corrigen valores vacíos o fuera de rango
    campo.addEventListener('change', () => {
        campo.value = leerCantidad(campo);
        actualizarResumen();
    });

    // Evitar submit accidental al tocar Enter dentro del input
    campo.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
        }
    });
});

// El navegador puede restaurar cantidades al volver atrás
window.addEventListener('pageshow', actualizarResumen);