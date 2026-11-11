/* Dialogo de confirmacion para cancelar la compra.
   La cancelacion la hace el servidor al recibir el formulario. */

const dialogoCancelacion = document.getElementById('dialogo-cancelacion');
const formularioCancelacion = document.getElementById('form-cancelacion');

document.getElementById('abrir-cancelacion').addEventListener('click', () => {
    dialogoCancelacion.showModal();
});

document.getElementById('cerrar-cancelacion').addEventListener('click', () => {
    dialogoCancelacion.close();
});

// Evita enviar dos veces la cancelacion por doble clic
formularioCancelacion.addEventListener('submit', () => {
    formularioCancelacion.querySelectorAll('button').forEach((boton) => {
        boton.disabled = true;
    });
});
