/* Carrusel visual. No realiza solicitudes de red: la API se consulta desde Flask/Python. */
document.addEventListener('DOMContentLoaded', () => {
  const carrusel = document.querySelector('[data-carrusel]');
  if (!carrusel) return;
  const slides = [...carrusel.querySelectorAll('[data-carrusel-slide]')];
  if (slides.length < 2) return;
  const puntos = [...carrusel.querySelectorAll('[data-carrusel-indice]')];
  const anterior = document.querySelector('[data-carrusel-anterior]');
  const siguiente = document.querySelector('[data-carrusel-siguiente]');
  const movimientoReducido = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  let indice = 0;
  let intervalo;

  function cambiar(nuevoIndice) {
    indice = (nuevoIndice + slides.length) % slides.length;
    slides.forEach((slide, i) => {
      const activo = i === indice;
      slide.classList.toggle('carrusel__slide--activo', activo);
      slide.setAttribute('aria-hidden', String(!activo));
      slide.querySelectorAll('a, button').forEach(el => { el.tabIndex = activo ? 0 : -1; });
    });
    puntos.forEach((punto, i) => {
      punto.classList.toggle('carrusel__punto--activo', i === indice);
      punto.setAttribute('aria-current', String(i === indice));
    });
  }
  function detener() { if (intervalo) clearInterval(intervalo); intervalo = undefined; }
  function iniciar() { detener(); if (!movimientoReducido && !document.hidden) intervalo = setInterval(() => cambiar(indice + 1), 5500); }
  anterior?.addEventListener('click', () => { cambiar(indice - 1); iniciar(); });
  siguiente?.addEventListener('click', () => { cambiar(indice + 1); iniciar(); });
  puntos.forEach(p => p.addEventListener('click', () => { cambiar(Number(p.dataset.carruselIndice)); iniciar(); }));
  carrusel.addEventListener('mouseenter', detener);
  carrusel.addEventListener('mouseleave', iniciar);
  carrusel.addEventListener('focusin', detener);
  carrusel.addEventListener('focusout', event => { if (!carrusel.contains(event.relatedTarget)) iniciar(); });
  document.addEventListener('visibilitychange', () => document.hidden ? detener() : iniciar());
  cambiar(0);
  iniciar();
});
