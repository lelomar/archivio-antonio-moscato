/* fuori linea (file://) Chrome non carica i caratteri da file: si usano quelli incorporati */
(function(){try{if(location.protocol==='file:'){var c=document.currentScript,l=document.createElement('link');l.rel='stylesheet';l.href=c.src.replace(/sito\.js(\?.*)?$/,'fonts/caratteri-offline.css');document.head.appendChild(l)}}catch(e){}})();
document.documentElement.classList.add('js');
/* scheda d'archivio: data di consultazione e copia delle citazioni */
document.addEventListener('DOMContentLoaded',function(){var M=['gennaio','febbraio','marzo','aprile','maggio','giugno','luglio','agosto','settembre','ottobre','novembre','dicembre'],d=new Date(),s=d.getDate()+' '+M[d.getMonth()]+' '+d.getFullYear();[].forEach.call(document.querySelectorAll('.consultato'),function(e){e.textContent=s})});
document.addEventListener('click',function(e){var b=e.target.closest&&e.target.closest('[data-copy-from]');if(!b)return;var el=document.querySelector(b.getAttribute('data-copy-from'));if(!el)return;var t=el.innerText.replace(/^APA\s+/,'').trim(),old=b.textContent;
function ok(){b.textContent='Copiata';setTimeout(function(){b.textContent=old},1800)}
if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(t).then(ok,function(){sel()})}else sel();
function sel(){var r=document.createRange();r.selectNodeContents(el);var g=getSelection();g.removeAllRanges();g.addRange(r);try{document.execCommand('copy');ok()}catch(x){}}});
/* note: richiamo [1] -> finestrella con il testo della nota, senza saltare in fondo alla pagina */
document.addEventListener('DOMContentLoaded',function(){
var T=document.querySelector('.testo');if(!T)return;var pop=null,cur=null;
function isNum(t){return /^\s*[\[(]?\s*(\d{1,3}|[ivxlc]{1,7})\s*[\])]?\s*$/i.test(t)}function lab(t){return t.replace(/[\[\]()\s]/g,'')}
function close(){if(pop){pop.remove();pop=null}if(cur){cur.setAttribute('aria-expanded','false');cur=null}}
var refs=[].slice.call(T.querySelectorAll('a[href^="#"]')).filter(function(a){
 var id=decodeURIComponent(a.getAttribute('href').slice(1));if(!id||!isNum(a.textContent))return false;
 var t=document.getElementById(id);if(!t||t===a)return false;
 if(!(a.compareDocumentPosition(t)&Node.DOCUMENT_POSITION_FOLLOWING))return false;
 a._nota=t;return true});
refs.forEach(function(a){a.classList.add('nref');a.setAttribute('aria-expanded','false');a.setAttribute('aria-label','Nota '+lab(a.textContent));
 a.addEventListener('click',function(e){e.preventDefault();if(cur===a){close();return}close();
  var blk=a._nota.closest('p,li,div')||a._nota.parentNode,c=blk.cloneNode(true);
  [].slice.call(c.querySelectorAll('a[href^="#"]')).forEach(function(x){if(isNum(x.textContent))x.remove()});
  [].slice.call(c.querySelectorAll('[id]')).forEach(function(x){x.removeAttribute('id')});
  pop=document.createElement('div');pop.className='notapop';pop.setAttribute('role','note');
  var h=document.createElement('div');h.className='np-h';h.innerHTML='<span>Nota '+lab(a.textContent)+'</span>';
  var go=document.createElement('a');go.href=a.getAttribute('href');go.textContent='tra le note';go.addEventListener('click',close);
  var x=document.createElement('button');x.type='button';x.className='np-x';x.setAttribute('aria-label','Chiudi la nota');x.textContent='×';x.addEventListener('click',function(){var r=cur;close();if(r)r.focus()});
  h.appendChild(go);h.appendChild(x);pop.appendChild(h);var b=document.createElement('div');b.className='np-b';b.innerHTML=c.innerHTML;pop.appendChild(b);
  document.body.appendChild(pop);var r=a.getBoundingClientRect(),w=pop.offsetWidth,vw=document.documentElement.clientWidth;
  var left=Math.max(12,Math.min(r.left+window.scrollX-24,vw-w-12+window.scrollX));
  pop.style.left=left+'px';pop.style.top=(r.bottom+window.scrollY+8)+'px';
  cur=a;a.setAttribute('aria-expanded','true');x.focus({preventScroll:true})});});
document.addEventListener('click',function(e){if(pop&&!pop.contains(e.target)&&!(e.target.closest&&e.target.closest('.nref')))close()});
document.addEventListener('keydown',function(e){if(e.key==='Escape'&&pop){var r=cur;close();if(r)r.focus()}});
window.addEventListener('resize',close);
});
document.addEventListener('DOMContentLoaded',function(){var b=document.querySelector('.hamb'),t=document.querySelector('.top');if(!b||!t)return;
b.addEventListener('click',function(){var o=t.classList.toggle('open');b.setAttribute('aria-expanded',o?'true':'false')});
document.addEventListener('keydown',function(e){if(e.key==='Escape'&&t.classList.contains('open')){t.classList.remove('open');b.setAttribute('aria-expanded','false');b.focus()}})});
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

/* Indice dei temi: filtro per tipo di entità (persona, organizzazione, luogo…) */
document.addEventListener('DOMContentLoaded',function(){var b=document.querySelector('.tipi'),w=document.querySelector('.tipi-f');if(!b||!w)return;
 function set(t){t=t||'';w.setAttribute('data-f',t);b.querySelectorAll('button').forEach(function(x){var on=(x.getAttribute('data-tipo')||'')===t;x.classList.toggle('on',on);x.setAttribute('aria-pressed',on?'true':'false')})}
 b.addEventListener('click',function(e){var x=e.target.closest('button');if(!x)return;set(x.getAttribute('data-tipo'));try{history.replaceState(null,'',x.getAttribute('data-tipo')?'#tipo-'+x.getAttribute('data-tipo'):location.pathname)}catch(_){}});
 var h=location.hash.match(/^#tipo-(.+)$/);set(h?decodeURIComponent(h[1]):'')});
