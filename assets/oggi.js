(function(){
var M=window.META;if(!M)return;
var BASE='https://lelomar.github.io/archivio-antonio-moscato/';
var MESI=['gennaio','febbraio','marzo','aprile','maggio','giugno','luglio','agosto','settembre','ottobre','novembre','dicembre'];
var PRE=document.body.getAttribute('data-pre')||'';
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function pad(n){return(n<10?'0':'')+n}
var BY={};M.arts.forEach(function(a){if(a[2]&&a[2].length>=10){var k=a[2].slice(5,10);(BY[k]=BY[k]||[]).push(a)}});
Object.keys(BY).forEach(function(k){BY[k].sort(function(x,y){return x[2]<y[2]?-1:1})});
function key(d){return pad(d.getMonth()+1)+'-'+pad(d.getDate())}
function label(k){var g=+k.slice(3);return(g==1?'1°':g)+' '+MESI[+k.slice(0,2)-1]}
function item(a,full){var y=a[2].slice(0,4),url=PRE+'articoli/'+a[0]+'.html';
 var h='<li class="entry"><div class="em"><span class="oy">'+y+'</span><a class="rb" href="'+PRE+'categorie/c'+a[3]+'.html">'+esc(M.cats[a[3]]||'')+'</a>'+(a[4]=='es'?'<span class="lg">ES</span>':'')+'</div><h3><a href="'+url+'">'+esc(a[1])+'</a></h3>';
 if(full&&a[6])h+='<p class="exc">'+esc(a[6])+'</p>';
 if(full){var gg=+a[2].slice(8,10);var txt='Accadde oggi. Il '+(gg==1?'1°':gg)+' '+MESI[+a[2].slice(5,7)-1]+' '+y+' Antonio Moscato pubblicava «'+a[1]+'». Dall’archivio ritrovato: '+BASE+'articoli/'+a[0]+'.html';
  h+='<button type="button" class="social-copy" data-copy="'+esc(txt)+'">Copia per i social</button>'}
 return h+'</li>'}
// riquadro in home
var box=document.getElementById('oggi');
if(box){var d=new Date(),k=key(d),L=BY[k]||[],near='';
 if(!L.length){for(var i=1;i<4&&!L.length;i++){var d2=new Date(d.getTime()-i*864e5);k=key(d2);L=BY[k]||[]}near=' (nei giorni vicini)'}
 var pick=L.slice().sort(function(){return Math.random()-.5}).slice(0,4).sort(function(x,y){return x[2]<y[2]?-1:1});
 box.innerHTML='<h2 class="sec">Accadde oggi · '+label(k)+near+'</h2><p class="lead">Cosa pubblicava Antonio Moscato sul suo sito in questo giorno, negli anni.</p><ul class="entries">'+pick.map(function(a){return item(a,false)}).join('')+'</ul><p class="more-l"><a href="'+PRE+'accadde-oggi.html#'+k+'">'+(L.length>pick.length?'Tutti i '+L.length+' testi di questo giorno':'Apri la rubrica')+' →</a></p>'}
// pagina dedicata
var pg=document.getElementById('oggi-pagina');
if(pg){var sm=document.getElementById('om'),sd=document.getElementById('od');
 sm.innerHTML=MESI.map(function(m,i){return'<option value="'+pad(i+1)+'">'+m+'</option>'}).join('');
 function days(){var n=new Date(2024,+sm.value,0).getDate(),v=sd.value;sd.innerHTML='';for(var i=1;i<=n;i++)sd.innerHTML+='<option value="'+pad(i)+'">'+i+'</option>';if(v&&+v<=n)sd.value=v}
 function show(k){sm.value=k.slice(0,2);days();sd.value=k.slice(3);
  var L=BY[k]||[];document.getElementById('ot').textContent=label(k);
  document.getElementById('on').textContent=L.length?(L.length+(L.length==1?' testo pubblicato':' testi pubblicati')+' in questo giorno, dal '+L[0][2].slice(0,4)+' al '+L[L.length-1][2].slice(0,4)):'Nessun testo in questo giorno.';
  document.getElementById('ol').innerHTML=L.map(function(a){return item(a,true)}).join('');
  try{history.replaceState(null,'','#'+k)}catch(e){location.hash=k}}
 function shift(n){var d=new Date(2024,+sm.value-1,+sd.value);d.setDate(d.getDate()+n);show(key(d))}
 sm.onchange=function(){days();show(sm.value+'-'+sd.value)};sd.onchange=function(){show(sm.value+'-'+sd.value)};
 document.getElementById('oprev').onclick=function(){shift(-1)};document.getElementById('onext').onclick=function(){shift(1)};
 document.getElementById('otoday').onclick=function(){show(key(new Date()))};
 var h=location.hash.slice(1);show(/^\d\d-\d\d$/.test(h)&&BY[h]!==undefined||/^\d\d-\d\d$/.test(h)?h:key(new Date()))}
})();
