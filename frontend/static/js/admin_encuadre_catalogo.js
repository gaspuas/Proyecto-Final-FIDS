"use strict";
(() => {
  for (const prefix of ['pelicula', 'funcion']) {
    const root = document.getElementById(prefix + '-encuadre');
    if (!root) continue;
    const byId = suffix => document.getElementById(prefix + '-' + suffix);
    const file = byId('imagen-archivo'), existing = byId('imagen-existente'), url = byId('imagen-url');
    const canvas = byId('encuadre-canvas'), ctx = canvas.getContext('2d');
    const zoom = byId('zoom'), zoomText = byId('zoom-valor'), center = byId('centrar'), apply = byId('aplicar');
    const empty = byId('encuadre-vacio'), status = byId('encuadre-estado');
    const form = root.closest('form'), movie = root.dataset.modo === 'funcion' ? document.getElementById('pelicula_id') : null;
    let img = null, blobUrl = null, generation = 0, dx = 0, dy = 0, factor = 1, drag = null, dirty = false, applied = false;
    const W = canvas.width, H = canvas.height;
    const notify = text => status.textContent = text;
    const geometry = () => {
      const ratio = Math.max(W / img.naturalWidth, H / img.naturalHeight) * factor;
      return {width: img.naturalWidth * ratio, height: img.naturalHeight * ratio};
    };
    function draw() {
      if (!img) return;
      const {width, height} = geometry();
      dx = Math.max((W-width)/2, Math.min((width-W)/2, dx));
      dy = Math.max((H-height)/2, Math.min((height-H)/2, dy));
      ctx.clearRect(0,0,W,H);
      ctx.drawImage(img,(W-width)/2+dx,(H-height)/2+dy,width,height);
    }
    function invalidate() { dirty = true; applied = false; notify('Encuadre pendiente: presioná Aplicar encuadre antes de guardar.'); }
    function release() { if (blobUrl) { URL.revokeObjectURL(blobUrl); blobUrl = null; } }
    function load(source, isLocal = false) {
      const current = ++generation;
      img = null; zoom.disabled = center.disabled = apply.disabled = true;
      empty.hidden = false; empty.textContent = 'Elegí una imagen para previsualizarla.';
      dirty = applied = false;
      if (!source) { notify('Elegí una imagen o utilizá el póster de la película.'); return; }
      const candidate = new Image();
      if (!isLocal && !source.startsWith('data:')) candidate.crossOrigin = 'anonymous';
      candidate.onload = () => {
        if (current !== generation) return;
        img = candidate; dx = dy = 0; factor = 1; zoom.value='100'; zoomText.value='100%';
        zoom.disabled = center.disabled = apply.disabled = false; empty.hidden = true; draw();
        notify('Imagen cargada. Podés arrastrarla y ajustar zoom; aplicá el encuadre si la editás.');
      };
      candidate.onerror = () => {
        if (current !== generation) return;
        empty.textContent = 'No se pudo previsualizar. La URL puede funcionar al guardar, pero para recortarla descargá la imagen y subila como archivo.';
        notify('No se puede previsualizar esta imagen.');
      };
      candidate.src = source;
    }
    function moviePoster() { return movie?.selectedOptions[0]?.dataset.poster || ''; }
    function selectSource(changed) {
      release();
      if (changed === 'file') {
        const f = file.files?.[0];
        if (f) {
          if (!/^image\/(jpeg|png|webp)$/.test(f.type) || f.size > 5*1024*1024) { file.value = ''; notify('Elegí JPG, PNG o WebP de hasta 5 MB.'); return; }
          existing.value = ''; url.value = '';
          blobUrl = URL.createObjectURL(f);
          load(blobUrl, true);
          return;
        }
      }
      if (changed === 'existing' && existing.value) { file.value = ''; url.value = ''; }
      if (changed === 'url' && url.value.trim()) { file.value = ''; existing.value = ''; }
      if (changed === 'movie') { file.value=''; existing.value=''; url.value=''; }
      if (file.files?.[0]) { blobUrl = URL.createObjectURL(file.files[0]); load(blobUrl,true); }
      else load(existing.value || url.value.trim() || moviePoster());
    }
    file.addEventListener('change',()=>selectSource('file'));
    existing.addEventListener('change',()=>selectSource('existing'));
    url.addEventListener('change',()=>selectSource('url'));
    if (movie) movie.addEventListener('change',()=>selectSource('movie'));
    zoom.addEventListener('input',()=>{if(!img)return;factor=Number(zoom.value)/100;zoomText.value=zoom.value+'%';draw();invalidate();});
    center.addEventListener('click',()=>{if(!img)return;dx=dy=0;factor=1;zoom.value='100';zoomText.value='100%';draw();invalidate();});
    canvas.addEventListener('pointerdown',e=>{if(!img)return;drag={id:e.pointerId,x:e.clientX,y:e.clientY};canvas.setPointerCapture(e.pointerId)});
    canvas.addEventListener('pointermove',e=>{if(!drag||drag.id!==e.pointerId)return;const rect=canvas.getBoundingClientRect();dx+=(e.clientX-drag.x)*W/rect.width;dy+=(e.clientY-drag.y)*H/rect.height;drag.x=e.clientX;drag.y=e.clientY;draw();invalidate()});
    for(const name of ['pointerup','pointercancel','lostpointercapture'])canvas.addEventListener(name,()=>drag=null);
    apply.addEventListener('click',()=>{
      if(!img)return;
      try {draw();canvas.toBlob(blob=>{
        if(!blob){notify('No se pudo exportar la imagen.');return;}
        if(blob.size>5*1024*1024){notify('El archivo recortado supera los 5 MB.');return;}
        const transfer = new DataTransfer();
        transfer.items.add(new File([blob],prefix+'_encuadrada.webp',{type:'image/webp'}));
        file.files=transfer.files;
        existing.value='';url.value='';dirty=false;applied=true;
        notify('✓ Encuadre aplicado. Al guardar, se almacenará una copia sin modificar el original.');
      },'image/webp',.88);} catch (_) {notify('La imagen externa no permite recortes. Descargala y subila como archivo.');}
    });
    form.addEventListener('submit',e=>{if(dirty&&!applied){e.preventDefault();notify('Aplicá el encuadre antes de guardar o volvé a elegir una imagen para descartarlo.');root.scrollIntoView({behavior:'smooth',block:'center'});}});
    selectSource('initial');
  }
})();
