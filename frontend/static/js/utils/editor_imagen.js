"use strict";
/*
 * Editor de encuadre compartido: Novedades, Películas y Funciones.
 * Configuración declarativa por ID para respetar los formularios Flask actuales.
 * No modifica archivos originales: el recorte genera un nuevo WebP en el input.
 */
(() => {
  const LIMITE_ARCHIVO = 5 * 1024 * 1024;
  const CONFIGURACIONES = [
    {
      raiz: 'admin-encuadre', archivo: 'imagen_archivo', existente: 'imagen_existente',
      canvas: 'admin-encuadre-canvas', zoom: 'admin-encuadre-zoom',
      valorZoom: 'admin-encuadre-zoom-valor', centrar: 'admin-encuadre-centrar',
      aplicar: 'admin-encuadre-aplicar', vacio: 'admin-encuadre-vacio',
      estado: 'admin-encuadre-estado', titulo: 'titulo', tituloVista: 'admin-encuadre-titulo',
      nombreSalida: 'novedad_encuadrada.webp', destino: 'novedades'
    },
    {
      raiz: 'pelicula-encuadre', archivo: 'pelicula-imagen-archivo',
      existente: 'pelicula-imagen-existente', url: 'pelicula-imagen-url',
      canvas: 'pelicula-encuadre-canvas', zoom: 'pelicula-zoom',
      valorZoom: 'pelicula-zoom-valor', centrar: 'pelicula-centrar',
      aplicar: 'pelicula-aplicar', vacio: 'pelicula-encuadre-vacio',
      estado: 'pelicula-encuadre-estado', titulo: 'titulo', tituloVista: 'pelicula-encuadre-titulo',
      nombreSalida: 'pelicula_encuadrada.webp', destino: 'peliculas'
    },
    {
      raiz: 'funcion-encuadre', archivo: 'funcion-imagen-archivo',
      existente: 'funcion-imagen-existente', url: 'funcion-imagen-url',
      canvas: 'funcion-encuadre-canvas', zoom: 'funcion-zoom',
      valorZoom: 'funcion-zoom-valor', centrar: 'funcion-centrar',
      aplicar: 'funcion-aplicar', vacio: 'funcion-encuadre-vacio',
      estado: 'funcion-encuadre-estado', pelicula: 'pelicula_id', tituloVista: 'funcion-encuadre-titulo',
      nombreSalida: 'funcion_encuadrada.webp', destino: 'funciones'
    }
  ];

  function iniciarEditor(config) {
    const raiz = document.getElementById(config.raiz);
    if (!raiz) return;
    const obtener = id => id ? document.getElementById(id) : null;
    const archivo = obtener(config.archivo);
    const existente = obtener(config.existente);
    const url = obtener(config.url);
    const pelicula = obtener(config.pelicula);
    const canvas = obtener(config.canvas);
    const zoom = obtener(config.zoom);
    const textoZoom = obtener(config.valorZoom);
    const centrar = obtener(config.centrar);
    const aplicar = obtener(config.aplicar);
    const vacio = obtener(config.vacio);
    const estado = obtener(config.estado);
    const formulario = raiz.closest('form');
    const marcaRecorte = raiz.querySelector('input[name=encuadre_aplicado]');
    const titulo = obtener(config.titulo);
    const tituloVista = obtener(config.tituloVista);
    if (![archivo, canvas, zoom, textoZoom, centrar, aplicar, vacio, estado, formulario].every(Boolean)) return;

    // Cartelera /peliculas/ y el editor comparten --cine-poster-proporcion.
    // No usamos una grilla ficticia ni una altura independiente del ancho:
    // eso producía una segunda pérdida del encuadre al mostrar el póster.
    function ajustarProporcion() {
      if (config.destino === 'peliculas') {
        const css = getComputedStyle(document.documentElement);
        const baseW = Number(css.getPropertyValue('--cine-poster-ancho').trim()) || 365;
        const baseH = Number(css.getPropertyValue('--cine-poster-alto').trim()) || 300;
        const nuevoAncho = Math.round(baseW * 2);
        const nuevoAlto = Math.round(baseH * 2);
        if (canvas.width !== nuevoAncho) canvas.width = nuevoAncho;
        if (canvas.height !== nuevoAlto) canvas.height = nuevoAlto;
        canvas.style.width = '100%';
        canvas.style.height = '100%';
        // La proporción visible es responsabilidad del CSS compartido.
        canvas.style.aspectRatio = 'auto';
        return;
      }
      // Funciones conserva su encuadre y presentación propios; Novedades no se toca.
      if (config.destino === 'funciones') {
        const visor = canvas.closest('.imagen-unificada__visor');
        const tarjetaVista = canvas.closest('.tarjeta-pelicula');
        const principal = document.querySelector('.contenedor-principal');
        let anchoTarjeta = 365, anchoPoster = 363, altoPoster = 300;
        if (principal) {
          const grilla = document.createElement('div');
          grilla.className = 'grilla-peliculas';
          grilla.style.cssText = 'visibility:hidden;height:0;overflow:hidden;pointer-events:none;';
          const tarjeta = document.createElement('article');
          tarjeta.className = 'tarjeta-pelicula';
          const poster = document.createElement('div');
          poster.className = 'tarjeta-pelicula__poster';
          tarjeta.appendChild(poster);
          grilla.appendChild(tarjeta);
          principal.appendChild(grilla);
          anchoTarjeta = tarjeta.getBoundingClientRect().width || anchoTarjeta;
          anchoPoster = poster.getBoundingClientRect().width || anchoPoster;
          altoPoster = poster.getBoundingClientRect().height || altoPoster;
          grilla.remove();
        }
        if (tarjetaVista) tarjetaVista.style.width = `${anchoTarjeta}px`;
        if (visor) {
          visor.style.width = '100%';
          visor.style.height = `${altoPoster}px`;
          visor.style.maxWidth = 'none';
        }
        const nuevoAncho = Math.round(anchoPoster * 2);
        const nuevoAlto = Math.round(altoPoster * 2);
        if (canvas.width !== nuevoAncho) canvas.width = nuevoAncho;
        if (canvas.height !== nuevoAlto) canvas.height = nuevoAlto;
        canvas.style.width = '100%';
        canvas.style.height = '100%';
        canvas.style.aspectRatio = 'auto';
      }
    }
    ajustarProporcion();
    const contexto = canvas.getContext('2d');
    if (!contexto) return;
    let W = canvas.width, H = canvas.height;
    let imagen = null, urlTemporal = null, secuencia = 0, arrastre = null;
    let desplazamientoX = 0, desplazamientoY = 0, escala = 1;
    let editado = false, aplicado = false, procesando = false, exportable = true;
    let temporizador = null;

    const avisar = texto => { estado.textContent = texto; };
    const habilitar = activo => {
      zoom.disabled = !activo || !exportable;
      centrar.disabled = !activo || !exportable;
      aplicar.disabled = !activo || !exportable || procesando;
    };
    const fijarZoom = valor => {
      zoom.value = String(valor);
      textoZoom.textContent = `${valor}%`;
      textoZoom.value = `${valor}%`;
    };
    const soltarURL = () => {
      if (urlTemporal) URL.revokeObjectURL(urlTemporal);
      urlTemporal = null;
    };
    const posterPelicula = () => pelicula?.selectedOptions[0]?.dataset.poster || '';
    const imagenActual = () => raiz.dataset.imagenActual || '';
    const fuenteElegida = () => existente?.value || url?.value.trim() || posterPelicula() || imagenActual();

    function tamano() {
      const factor = Math.max(W / imagen.naturalWidth, H / imagen.naturalHeight) * escala;
      return { ancho: imagen.naturalWidth * factor, alto: imagen.naturalHeight * factor };
    }
    function dibujar() {
      if (!imagen) return;
      const { ancho, alto } = tamano();
      desplazamientoX = Math.max(-(ancho-W)/2, Math.min((ancho-W)/2, desplazamientoX));
      desplazamientoY = Math.max(-(alto-H)/2, Math.min((alto-H)/2, desplazamientoY));
      contexto.clearRect(0, 0, W, H);
      contexto.drawImage(imagen, (W-ancho)/2 + desplazamientoX, (H-alto)/2 + desplazamientoY, ancho, alto);
    }
    function marcarEdicion() {
      if (marcaRecorte) marcaRecorte.value = '0';
      editado = true;
      aplicado = false;
      avisar('Encuadre pendiente: presioná «Aplicar encuadre» antes de guardar.');
    }
    function cargarFuente(origen, esArchivo = false) {
      if (marcaRecorte) marcaRecorte.value = '0';
      const turno = ++secuencia;
      imagen = null; arrastre = null; editado = aplicado = procesando = false;
      exportable = true;
      habilitar(false);
      vacio.hidden = false;
      vacio.style.display = '';
      vacio.textContent = 'Elegí una imagen para previsualizarla.';
      // Reiniciar el canvas elimina el bloqueo de seguridad de una URL externa previa.
      canvas.width = W;
      if (!origen) {
        avisar('Elegí una imagen para empezar.');
        return;
      }

      function lista(permitirRecorte, foto) {
        if (turno !== secuencia) return;
        imagen = foto;
        exportable = permitirRecorte;
        desplazamientoX = desplazamientoY = 0;
        escala = 1;
        fijarZoom(100);
        vacio.hidden = true;
        vacio.style.display = 'none'; // también corrige un CSS anterior que anulaba [hidden]
        dibujar();
        habilitar(true);
        avisar(permitirRecorte
          ? 'Imagen lista. Arrastrala para moverla, ajustá el zoom y aplicá el encuadre si lo modificás.'
          : 'Vista previa disponible, pero esta URL no permite recortar. Descargá la imagen y subila como archivo para editarla.');
      }

      const foto = new Image();
      const externa = !esArchivo && /^https?:\/\//i.test(origen) && new URL(origen, location.href).origin !== location.origin;
      if (externa) foto.crossOrigin = 'anonymous';
      foto.onload = () => lista(true, foto);
      foto.onerror = () => {
        if (turno !== secuencia) return;
        if (externa) {
          // Mostrar sin CORS es posible, pero exportar un canvas contaminado no.
          const soloVista = new Image();
          soloVista.onload = () => lista(false, soloVista);
          soloVista.onerror = () => {
            if (turno === secuencia) {
              vacio.textContent = 'No se pudo cargar esta imagen.';
              avisar('La imagen no está disponible. Probá con un archivo o una imagen del proyecto.');
            }
          };
          soloVista.src = origen;
        } else {
          vacio.textContent = 'No se pudo cargar esta imagen.';
          avisar('Verificá la imagen elegida o subí otra.');
        }
      };
      foto.src = origen;
    }

    function elegirFuente(tipo) {
      if (tipo !== 'url') clearTimeout(temporizador);
      soltarURL();
      if (tipo === 'archivo') {
        const seleccion = archivo.files?.[0];
        if (seleccion) {
          if (!['image/jpeg', 'image/png', 'image/webp'].includes(seleccion.type)) {
            archivo.value = '';
            avisar('Elegí un archivo JPG, PNG o WebP.');
            cargarFuente(fuenteElegida());
            return;
          }
          if (seleccion.size > LIMITE_ARCHIVO) {
            archivo.value = '';
            avisar('La imagen supera el límite de 5 MB.');
            cargarFuente(fuenteElegida());
            return;
          }
          if (existente) existente.value = '';
          if (url) url.value = '';
          urlTemporal = URL.createObjectURL(seleccion);
          cargarFuente(urlTemporal, true);
          return;
        }
      } else if (tipo === 'existente') {
        archivo.value = '';
        if (url) url.value = '';
      } else if (tipo === 'url') {
        archivo.value = '';
        if (existente) existente.value = '';
      } else if (tipo === 'pelicula') {
        // Si se cambia de película se vuelve a mostrar su póster como base.
        archivo.value = '';
        if (existente) existente.value = '';
        if (url) url.value = '';
      }
      cargarFuente(fuenteElegida());
    }

    archivo.addEventListener('change', () => elegirFuente('archivo'));
    existente?.addEventListener('change', () => elegirFuente('existente'));
    if (url) {
      url.addEventListener('input', () => {
        clearTimeout(temporizador);
        temporizador = setTimeout(() => elegirFuente('url'), 450);
      });
      url.addEventListener('change', () => {
        clearTimeout(temporizador);
        elegirFuente('url');
      });
    }
    pelicula?.addEventListener('change', () => {
      if (tituloVista) tituloVista.textContent = pelicula.selectedOptions[0]?.textContent.trim() || 'Tu película';
      elegirFuente('pelicula');
    });

    zoom.addEventListener('input', () => {
      if (!imagen) return;
      escala = Number(zoom.value) / 100;
      fijarZoom(Number(zoom.value));
      dibujar();
      marcarEdicion();
    });
    centrar.addEventListener('click', () => {
      if (!imagen) return;
      desplazamientoX = desplazamientoY = 0;
      escala = 1;
      fijarZoom(100);
      dibujar();
      marcarEdicion();
    });
    canvas.addEventListener('pointerdown', event => {
      if (!imagen || !exportable || procesando) return;
      arrastre = { id: event.pointerId, x: event.clientX, y: event.clientY };
      canvas.setPointerCapture(event.pointerId);
    });
    canvas.addEventListener('pointermove', event => {
      if (!arrastre || arrastre.id !== event.pointerId || !imagen) return;
      const limites = canvas.getBoundingClientRect();
      const anteriorX = desplazamientoX, anteriorY = desplazamientoY;
      desplazamientoX += (event.clientX - arrastre.x) * W / limites.width;
      desplazamientoY += (event.clientY - arrastre.y) * H / limites.height;
      arrastre.x = event.clientX;
      arrastre.y = event.clientY;
      dibujar();
      if (Math.abs(desplazamientoX-anteriorX) + Math.abs(desplazamientoY-anteriorY) > 0.25) {
        marcarEdicion();
      } else if (!editado) {
        avisar('La imagen ya cubre todo el espacio en esa dirección. Aumentá el zoom para poder moverla.');
      }
    });
    ['pointerup', 'pointercancel', 'lostpointercapture'].forEach(evento =>
      canvas.addEventListener(evento, () => { arrastre = null; }));

    aplicar.addEventListener('click', () => {
      if (!imagen || !exportable || procesando) return;
      procesando = true;
      habilitar(true);
      avisar('Preparando imagen recortada…');
      try {
        dibujar();
        canvas.toBlob(blob => {
          procesando = false;
          if (!blob || blob.size > LIMITE_ARCHIVO) {
            habilitar(true);
            avisar(blob ? 'La imagen recortada supera los 5 MB.' : 'No se pudo generar la imagen recortada.');
            return;
          }
          try {
            const envio = new DataTransfer();
            envio.items.add(new File([blob], config.nombreSalida, { type: 'image/webp' }));
            archivo.files = envio.files;
          } catch (_) {
            habilitar(true);
            avisar('Tu navegador no permite adjuntar el recorte. Probá con Chrome o Edge actualizado.');
            return;
          }
          if (existente) existente.value = '';
          if (url) url.value = '';
          aplicado = true;
          editado = false;
          if (marcaRecorte) marcaRecorte.value = '1';
          habilitar(true);
          avisar(`✓ Encuadre aplicado. Al guardar, se guardará una copia en la carpeta de ${config.destino}.`);
        }, 'image/webp', 0.88);
      } catch (_) {
        procesando = false;
        exportable = false;
        habilitar(true);
        avisar('Esta URL impide guardar el recorte. Descargá la imagen y subila como archivo.');
      }
    });
    formulario.addEventListener('submit', evento => {
      if (marcaRecorte?.value === '1' && !(archivo.files?.[0]?.type === 'image/webp')) {
        evento.preventDefault();
        avisar('El recorte no quedó adjuntado. Volvé a presionar «Aplicar encuadre».');
        raiz.scrollIntoView({ behavior: 'smooth', block: 'center' });
        return;
      }
      if (procesando || (editado && !aplicado)) {
        evento.preventDefault();
        avisar('Antes de guardar, presioná «Aplicar encuadre» o elegí nuevamente la imagen para descartar los ajustes.');
        raiz.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    });
    titulo?.addEventListener('input', () => {
      if (tituloVista) tituloVista.textContent = titulo.value || 'Tu promoción';
    });
    // Si cambia el ancho de las tarjetas, el recorte cambia de dimensiones también.
    // Volver a aplicarlo evita una imagen que parezca correcta pero llegue reencuadrada.
    if (config.destino === 'peliculas' || config.destino === 'funciones') {
      let ultimoAncho = W, ultimoAlto = H;
      window.addEventListener('resize', () => {
        ajustarProporcion();
        if (canvas.width === ultimoAncho && canvas.height === ultimoAlto) return;
        ultimoAncho = W = canvas.width;
        ultimoAlto = H = canvas.height;
        if (imagen) { dibujar(); marcarEdicion(); }
      });
    }
    // Previsualización inicial: misma fuente que se enviará al guardar.
    elegirFuente('inicial');
    window.addEventListener('pagehide', soltarURL, { once: true });
  }

  CONFIGURACIONES.forEach(iniciarEditor);
})();
