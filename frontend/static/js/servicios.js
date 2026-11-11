/* Total estimado del resumen al cambiar las cantidades.
   Es solo orientativo: el importe definitivo lo devuelve la API al confirmar. */

const formularioServicios = document.getElementById('form-servicios');
const totalEntradas = Number(formularioServicios.dataset.totalEntradas);
const cantidades = Array.from(formularioServicios.querySelectorAll('.servicios-lista__cantidad'));
const resumenServicios = document.getElementById('resumen-servicios');
const resumenTotal = document.getElementById('resumen-total');
const botonConfirmar = formularioServicios.querySelector('button[type="submit"]');

function leerCantidad(campo) {
    const cantidad = Number.parseInt(campo.value, 10);
    if (Number.isNaN(cantidad)) {
        return 0;
    }
    return Math.min(Math.max(cantidad, 0), Number(campo.max));
}

// Mismo formato que el filtro "precio" de Flask: sin decimales si el importe es entero
function formatearImporte(importe) {
    return Number.isInteger(importe) ? String(importe) : importe.toFixed(2);
}

function actualizarResumen() {
    const totalServicios = cantidades.reduce(
        (total, campo) => total + leerCantidad(campo) * Number(campo.dataset.precio),
        0,
    );
    resumenServicios.textContent = formatearImporte(totalServicios);
    resumenTotal.textContent = formatearImporte(totalEntradas + totalServicios);
}

cantidades.forEach((campo) => {
    campo.addEventListener('input', actualizarResumen);

    // Al salir del campo se corrigen valores vacios o fuera de rango
    campo.addEventListener('change', () => {
        campo.value = leerCantidad(campo);
        actualizarResumen();
    });
});

// Evita confirmar dos veces la misma compra por doble clic
formularioServicios.addEventListener('submit', () => {
    cantidades.forEach((campo) => {
        campo.value = leerCantidad(campo);
    });
    botonConfirmar.disabled = true;
    botonConfirmar.textContent = 'Confirmando…';
});

// El navegador puede restaurar cantidades o el boton deshabilitado al volver atras
window.addEventListener('pageshow', () => {
    botonConfirmar.disabled = false;
    botonConfirmar.textContent = 'Confirmar compra';
    actualizarResumen();
});
