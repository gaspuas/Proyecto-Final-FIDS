"use strict";
(() => {
  const root = document.getElementById('admin-encuadre');
  if (!root) return;
  const fileInput = document.getElementById('imagen_archivo');
  const existing = document.getElementById('imagen_existente');
  const canvas = document.getElementById('admin-encuadre-canvas');
  const ctx = canvas.getContext('2d');
  const zoom = document.getElementById('admin-encuadre-zoom');
  const zoomText = document.getElementById('admin-encuadre-zoom-valor');
  const center = document.getElementById('admin-encuadre-centrar');
  const apply = document.getElementById('admin-encuadre-aplicar');
  const empty = document.getElementById('admin-encuadre-vacio');
  const status = document.getElementById('admin-encuadre-estado');
  const form = root.closest('form');
  const titleInput = document.getElementById('titulo');
  const titlePreview = document.getElementById('admin-encuadre-titulo');
  let img = null, objectUrl = null, generation = 0;
  let offsetX = 0, offsetY = 0, scaleExtra = 1, pointer = null, changed = false;
  let appliedFile = null;
  const W = canvas.width, H = canvas.height;

  function notify(message) { status.textContent = message; }
  function dimensions() {
    const base = Math.max(W / img.naturalWidth, H / img.naturalHeight);
    const scale = base * scaleExtra;
    return { w: img.naturalWidth * scale, h: img.naturalHeight * scale };
  }
  function clampOffsets() {
    const {w, h} = dimensions();
    offsetX = Math.max(-(w-W)/2, Math.min((w-W)/2, offsetX));
    offsetY = Math.max(-(h-H)/2, Math.min((h-H)/2, offsetY));
  }
  function draw() {
    if (!img) return;
    clampOffsets();
    const {w,h} = dimensions();
    ctx.clearRect(0, 0, W, H);
    ctx.drawImage(img, (W-w)/2+offsetX, (H-h)/2+offsetY, w, h);
  }
  function invalidate() {
    if (appliedFile) {
      // After editing again, restore source selection rather than submitting an outdated crop.
      appliedFile = null;
      if (existing && existing.value) fileInput.value = '';
    }
    changed = true;
    apply.disabled = !img;
    notify('Encuadre pendiente. Tocá «Aplicar encuadre» para guardarlo.');
  }
  async function loadSource(src, isFile) {
    const id = ++generation;
    if (objectUrl) { URL.revokeObjectURL(objectUrl); objectUrl = null; }
    img = null; pointer = null;
    zoom.disabled = center.disabled = apply.disabled = true;
    empty.hidden = false;
    if (!src) { notify('Seleccioná una imagen para empezar.'); return; }
    const picture = new Image();
    if (!isFile && !src.startsWith('data:')) picture.crossOrigin = 'anonymous';
    picture.onload = () => {
      if (id !== generation) return;
      img = picture; offsetX = offsetY = 0; scaleExtra = 1; zoom.value = '100'; zoomText.value = '100%';
      empty.hidden = true; zoom.disabled = center.disabled = apply.disabled = false;
      changed = false; appliedFile = null; draw();
      notify('Arrastrá la imagen para moverla, ajustá el zoom y presioná «Aplicar encuadre».');
    };
    picture.onerror = () => { if (id === generation) { empty.textContent = 'No se pudo cargar esta imagen. Podés descargarla y subirla como archivo.'; notify('No se pudo previsualizar esta imagen.'); } };
    picture.src = src;
  }
  function changeFile() {
    const file = fileInput.files && fileInput.files[0];
    if (!file) return;
    if (!/^image\/(jpeg|png|webp)$/.test(file.type)) { notify('Elegí una imagen JPG, PNG o WebP.'); return; }
    if (file.size > 5*1024*1024) { notify('La imagen supera el límite de 5 MB.'); return; }
    if (existing) existing.value = '';
    objectUrl = URL.createObjectURL(file);
    loadSourceKeepingObjectUrl(objectUrl);
  }
  function loadSourceKeepingObjectUrl(url) {
    // loadSource would revoke the new blob URL; hand it ownership afterwards.
    objectUrl = null;
    loadSource(url, true);
    objectUrl = url;
  }
  fileInput.addEventListener('change', changeFile);
  if (existing) existing.addEventListener('change', () => {
    const url = existing.value || root.dataset.imagenActual;
    fileInput.value = '';
    loadSource(url, false);
  });
  zoom.addEventListener('input', () => {
    if (!img) return;
    scaleExtra = Number(zoom.value)/100;
    zoomText.value = zoom.value+'%';
    draw(); invalidate();
  });
  center.addEventListener('click', () => {
    if (!img) return;
    offsetX = offsetY = 0; scaleExtra = 1; zoom.value = '100'; zoomText.value = '100%';
    draw(); invalidate();
  });
  canvas.addEventListener('pointerdown', e => {
    if (!img) return;
    pointer = {id:e.pointerId, x:e.clientX, y:e.clientY};
    canvas.setPointerCapture(e.pointerId);
  });
  canvas.addEventListener('pointermove', e => {
    if (!pointer || pointer.id !== e.pointerId || !img) return;
    const rect = canvas.getBoundingClientRect();
    offsetX += (e.clientX-pointer.x) * W/rect.width;
    offsetY += (e.clientY-pointer.y) * H/rect.height;
    pointer.x = e.clientX; pointer.y = e.clientY;
    draw(); invalidate();
  });
  for (const event of ['pointerup','pointercancel','lostpointercapture']) {
    canvas.addEventListener(event, () => { pointer = null; });
  }
  apply.addEventListener('click', () => {
    if (!img) return;
    try {
      draw();
      canvas.toBlob(blob => {
        if (!blob) { notify('No se pudo generar la imagen.'); return; }
        if (blob.size > 5*1024*1024) { notify('La imagen generada supera 5 MB.'); return; }
        const transfer = new DataTransfer();
        const file = new File([blob], 'novedad_encuadrada.webp', {type:'image/webp'});
        transfer.items.add(file);
        fileInput.files = transfer.files;
        appliedFile = file;
        changed = false;
        notify('✓ Encuadre aplicado. Al guardar la novedad, se subirá esta imagen a la carpeta de novedades.');
      }, 'image/webp', .88);
    } catch (err) {
      notify('Este enlace de imagen no permite recortarla desde el navegador. Descargá la foto y subila como archivo para editarla.');
    }
  });
  form.addEventListener('submit', event => {
    if (changed && img && !appliedFile) {
      event.preventDefault(); notify('Aplicá el encuadre antes de guardar o presioná «Centrar» y después «Aplicar encuadre».');
      root.scrollIntoView({behavior:'smooth', block:'center'});
    }
  });
  if (titleInput) titleInput.addEventListener('input', () => { titlePreview.textContent = titleInput.value || 'Tu promoción'; });
  if (existing && existing.value) loadSource(existing.value, false);
  else if (root.dataset.imagenActual) loadSource(root.dataset.imagenActual, false);
})();
