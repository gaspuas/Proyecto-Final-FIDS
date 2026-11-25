document.addEventListener('DOMContentLoaded', () => {
  const formulario = document.querySelector('.tarjeta-funciones form');
  const precioEntrada = formulario?.querySelector('[data-precio-entrada]');
  if (!formulario || !precioEntrada) return;

  function actualizarPrecio() {
    const seleccionada = formulario.querySelector('input[name="funcion_id"]:checked');
    const precio = Number(seleccionada?.dataset.precio);
    if (Number.isFinite(precio)) {
      precioEntrada.textContent = precio.toFixed(2);
    }
  }

  formulario.addEventListener('change', event => {
    if (event.target.matches('input[name="funcion_id"]')) actualizarPrecio();
  });

  actualizarPrecio();
});
