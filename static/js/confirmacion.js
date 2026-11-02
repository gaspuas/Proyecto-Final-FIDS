/* Cancelacion simulada: solo cambia lo que se ve, no se guarda en ningun lado. */

const dialogoCancelacion = document.getElementById('dialogo-cancelacion');

document.getElementById('abrir-cancelacion').addEventListener('click', () => {
    dialogoCancelacion.showModal();
});

document.getElementById('cerrar-cancelacion').addEventListener('click', () => {
    dialogoCancelacion.close();
});

document.getElementById('confirmar-cancelacion').addEventListener('click', () => {
    dialogoCancelacion.close();

    document.getElementById('confirmacion').classList.add('confirmacion--cancelada');
    document.getElementById('confirmacion-titulo').textContent = 'Compra cancelada';
    document.getElementById('confirmacion-qr').alt = 'Código QR de demostración anulado';
    document.getElementById('confirmacion-acciones').hidden = true;
    document.getElementById('confirmacion-cancelada').hidden = false;
});
