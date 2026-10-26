(function(){
function P(){return document.body.getAttribute('data-pre')||''}
var MAP={};'àáâãäå:a,èéêë:e,ìíîï:i,òóôõö:o,ùúûü:u,ç:c,ñ:n,ý:y,œ:o,æ:a,ß:s'.split(',').forEach(function(p){var a=p.split(':');for(var i=0;i<a[0].length;i++)MAP[a[0][i]]=a[1]});
window.fold=function(s){return (s||'').toLowerCase().replace(/[^a-z0-9 ]/g,function(c){return MAP[c]||' '})};
window.miniCerca=function(f){var q=f.q.value.trim();location.href=P()+'cerca.html#q='+encodeURIComponent(q);return false};
window.filtra=function(v){var w=fold(v).split(/\s+/).filter(Boolean),n=0,tot=0;
 document.querySelectorAll('.entry[data-t]').forEach(function(e){var t=e.getAttribute('data-t'),ok=w.every(function(x){return t.indexOf(x)>=0});e.style.display=ok?'':'none';tot++;if(ok)n++});
 document.querySelectorAll('.ygroup').forEach(function(g){var vis=g.querySelector('.entry:not([style*="none"])');g.style.display=vis?'':'none'});
 var j=document.querySelector('.jump');if(j)j.style.display=w.length?'none':'';
 var c=document.getElementById('fcount');if(c)c.textContent=w.length?(n+' di '+tot):''};
function getfs(){try{return parseFloat(localStorage.getItem('fs'))||1}catch(e){return 1}}
window.fs=function(d){var v=Math.min(1.6,Math.max(0.8,getfs()+d*0.1));try{localStorage.setItem('fs',v)}catch(e){}apply()};
function apply(){var t=document.getElementById('testo');if(t)t.style.fontSize=getfs()+'em'}
document.addEventListener('DOMContentLoaded',function(){apply();
window.aCaso=function(){if(!window.META)return true;var a=META.arts[Math.floor(Math.random()*META.arts.length)];location.href=P()+'articoli/'+a[0]+'.html';return false};
var pg=document.getElementById('prog');
if(document.body.classList.contains('pg-art')&&pg){window.addEventListener('scroll',function(){var h=document.documentElement;var p=h.scrollTop/(h.scrollHeight-h.clientHeight||1);pg.style.width=(p*100)+'%'},{passive:true})}
});
})();
(function(){
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
var box=null,last=null;
function close(){if(!box)return;box.remove();box=null;document.documentElement.classList.remove('modal-open');if(last)last.focus()}
function openPdf(href,title){
 last=document.activeElement;close();
 var name=decodeURIComponent(href.split('/').pop().split('#')[0]);
 box=document.createElement('div');box.className='pdfmodal';box.setAttribute('role','dialog');box.setAttribute('aria-modal','true');box.setAttribute('aria-label','Documento PDF: '+(title||name));
 box.innerHTML='<div class="pm-back"></div><div class="pm-win"><div class="pm-bar"><span class="pm-t">'+esc(title||name)+'</span>'+
  '<a class="pm-b" href="'+esc(href)+'" download="'+esc(name)+'">Scarica</a><a class="pm-b" href="'+esc(href)+'" target="_blank" rel="noopener">Nuova scheda</a>'+
  '<button class="pm-x" aria-label="Chiudi">✕</button></div><iframe class="pm-f" src="'+esc(href)+'#view=FitH" title="'+esc(title||name)+'"></iframe></div>';
 document.body.appendChild(box);document.documentElement.classList.add('modal-open');
 box.querySelector('.pm-back').onclick=close;box.querySelector('.pm-x').onclick=close;box.querySelector('.pm-x').focus()}
window.apriPdf=openPdf;
document.addEventListener('keydown',function(e){if(e.key==='Escape')close()});
document.addEventListener('click',function(e){
 var a=e.target.closest&&e.target.closest('a[href]');if(!a||a.hasAttribute('download')||a.target==='_blank'&&!a.hasAttribute('data-pdf'))return;
 var h=a.getAttribute('href');if(!/\.pdf(#.*)?$/i.test(h)||/^[a-z]+:/i.test(h))return;
 if(e.metaKey||e.ctrlKey||e.shiftKey||window.innerWidth<640)return;
 e.preventDefault();openPdf(h,a.getAttribute('data-title')||a.textContent.trim())});
})();
document.addEventListener('click',function(e){var b=e.target.closest&&e.target.closest('[data-copy]');if(!b)return;var u=b.getAttribute('data-copy');
 function ok(){var t=b.textContent;b.textContent='Copiato ✓';setTimeout(function(){b.textContent=t},1800)}
 if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(u).then(ok,function(){prompt('Copia il link:',u)})}else{prompt('Copia il link:',u)}});
