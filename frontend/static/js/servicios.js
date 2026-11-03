/* Recalcula el resumen de la compra al cambiar las cantidades. */

const formularioServicios = document.getElementById('form-servicios');
const totalEntradas = Number(formularioServicios.dataset.totalEntradas);
const cantidades = Array.from(formularioServicios.querySelectorAll('.servicios-lista__cantidad'));
const resumenServicios = document.getElementById('resumen-servicios');
const resumenTotal = document.getElementById('resumen-total');

function leerCantidad(campo) {
    const cantidad = Number.parseInt(campo.value, 10);
    if (Number.isNaN(cantidad)) {
        return 0;
    }
    return Math.min(Math.max(cantidad, 0), Number(campo.max));
}

function actualizarResumen() {
    const totalServicios = cantidades.reduce(
        (total, campo) => total + leerCantidad(campo) * Number(campo.dataset.precio),
        0,
    );
    resumenServicios.textContent = totalServicios;
    resumenTotal.textContent = totalEntradas + totalServicios;
}

cantidades.forEach((campo) => {
    campo.addEventListener('input', actualizarResumen);

    // Al salir del campo se corrigen valores vacios o fuera de rango
    campo.addEventListener('change', () => {
        campo.value = leerCantidad(campo);
        actualizarResumen();
    });
});

// El navegador puede restaurar cantidades al volver atras
window.addEventListener('pageshow', actualizarResumen);
