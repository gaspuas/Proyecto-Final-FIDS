"use strict";
(()=>{
 const root=document.getElementById('funcion-encuadre');if(!root)return;
 const select=document.getElementById('pelicula_id'),file=document.getElementById('funcion_imagen');
 const canvas=document.getElementById('funcion-encuadre-canvas'),ctx=canvas.getContext('2d'),zoom=document.getElementById('funcion-zoom'),value=document.getElementById('funcion-zoom-valor');
 const center=document.getElementById('funcion-centrar'),apply=document.getElementById('funcion-aplicar'),empty=document.getElementById('funcion-encuadre-vacio'),status=document.getElementById('funcion-encuadre-estado');
 const form=root.closest('form'),W=canvas.width,H=canvas.height;
 let img=null,sourceUrl=null,token=0,dx=0,dy=0,zoomFactor=1,drag=null,dirty=false,applied=false,sourceFile=null;
 const info=s=>{status.textContent=s};
 const geom=()=>{const scale=Math.max(W/img.naturalWidth,H/img.naturalHeight)*zoomFactor;return {w:img.naturalWidth*scale,h:img.naturalHeight*scale}};
 function draw(){if(!img)return;const {w,h}=geom();dx=Math.max(-(w-W)/2,Math.min((w-W)/2,dx));dy=Math.max(-(h-H)/2,Math.min((h-H)/2,dy));ctx.clearRect(0,0,W,H);ctx.drawImage(img,(W-w)/2+dx,(H-h)/2+dy,w,h)}
 function mark(){dirty=true;applied=false;info('Encuadre pendiente: presioná Aplicar encuadre antes de guardar.')}
 function load(url,local=false){const id=++token;img=null;zoom.disabled=center.disabled=apply.disabled=true;empty.hidden=false;if(!url){info('Elegí una película con póster o subí una imagen.');return}const im=new Image();if(!local&&!url.startsWith('data:'))im.crossOrigin='anonymous';im.onload=()=>{if(id!==token)return;img=im;dx=dy=0;zoomFactor=1;zoom.value='100';value.textContent='100%';zoom.disabled=center.disabled=apply.disabled=false;empty.hidden=true;dirty=false;applied=false;draw();info('Mové la imagen arrastrando, ajustá el zoom y aplicá el encuadre si querés conservarlo.')};im.onerror=()=>{if(id!==token)return;empty.textContent='La foto no se pudo cargar. Podés guardarla y subirla como archivo.';info('La imagen externa no permite previsualizarse. Descargala y subila como archivo.')};im.src=url}
 function release(){if(sourceUrl){URL.revokeObjectURL(sourceUrl);sourceUrl=null}}
 function changeMovie(){release();file.value='';sourceFile=null;load(select.selectedOptions[0]?.dataset.poster||'')}
 select.addEventListener('change',changeMovie);
 file.addEventListener('change',()=>{const f=file.files?.[0];if(!f){changeMovie();return}if(!/^image\/(jpeg|png|webp)$/.test(f.type)||f.size>5*1024*1024){file.value='';info('Elegí un archivo JPG, PNG o WebP de hasta 5 MB.');return}release();sourceFile=f;sourceUrl=URL.createObjectURL(f);load(sourceUrl,true)});
 zoom.addEventListener('input',()=>{if(!img)return;zoomFactor=Number(zoom.value)/100;value.textContent=zoom.value+'%';draw();mark()});
 center.addEventListener('click',()=>{if(!img)return;dx=dy=0;zoomFactor=1;zoom.value='100';value.textContent='100%';draw();mark()});
 canvas.addEventListener('pointerdown',e=>{if(!img)return;drag={id:e.pointerId,x:e.clientX,y:e.clientY};canvas.setPointerCapture(e.pointerId)});
 canvas.addEventListener('pointermove',e=>{if(!drag||drag.id!==e.pointerId)return;const b=canvas.getBoundingClientRect();dx+=(e.clientX-drag.x)*W/b.width;dy+=(e.clientY-drag.y)*H/b.height;drag.x=e.clientX;drag.y=e.clientY;draw();mark()});
 for(const e of ['pointerup','pointercancel','lostpointercapture'])canvas.addEventListener(e,()=>drag=null);
 apply.addEventListener('click',()=>{if(!img)return;try{draw();canvas.toBlob(blob=>{if(!blob){info('No se pudo exportar la imagen.');return}if(blob.size>5*1024*1024){info('La imagen recortada supera 5 MB.');return}const transfer=new DataTransfer();transfer.items.add(new File([blob],'funcion_encuadrada.webp',{type:'image/webp'}));file.files=transfer.files;applied=true;dirty=false;info('✓ Encuadre aplicado. La imagen se guardará al crear la función.')},'image/webp',.88)}catch(e){info('Este enlace no admite recortes. Descargá la imagen y subila desde tu computadora.')}});
 form.addEventListener('submit',e=>{if(dirty&&!applied){e.preventDefault();info('Aplicá el encuadre antes de guardar, o volvé a elegir la película para descartarlo.');root.scrollIntoView({behavior:'smooth',block:'center'})}});
 changeMovie();
})();
