(function(){
var M=window.META,AR=M.arts,CATS=M.cats,KWN=M.kwn,KWS=M.kwslug;
var MESI=['gennaio','febbraio','marzo','aprile','maggio','giugno','luglio','agosto','settembre','ottobre','novembre','dicembre'];
function hd(d){return d&&d.length>=10?(+d.slice(8,10))+' '+MESI[+d.slice(5,7)-1]+' '+d.slice(0,4):''}
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function $(i){return document.getElementById(i)}
var R=AR.map(function(a){return{id:a[0],t:a[1],d:a[2],y:a[2].slice(0,4),c:String(a[3]),l:a[4],k:a[5],e:a[6],w:a[7],ft:fold(a[1]),fk:' '+a[5].join(' | ')+' ',fe:fold(a[6])}});
M.docs.forEach(function(a){R.push({id:a[0],t:a[1],d:a[2],y:a[2].slice(0,4),c:'doc',l:a[4],k:[],e:a[6],w:a[7],href:a[8],sub:a[9],ext:a[10],ft:fold(a[1]),fk:' '+fold(a[9])+' ',fe:fold(a[6])})});
var YEARS=[];R.forEach(function(r){if(r.y&&YEARS.indexOf(r.y)<0)YEARS.push(r.y)});YEARS.sort();
var TX=null,FT=null,loading=false;
var st={q:'',dove:'all',ord:'rel',y1:'',y2:'',cat:[],lang:[],tema:[],p:1};
function readHash(){var h=location.hash.slice(1);st={q:'',dove:'all',ord:'rel',y1:'',y2:'',cat:[],lang:[],tema:[],p:1};
 h.split('&').forEach(function(kv){if(!kv)return;var i=kv.indexOf('='),k=kv.slice(0,i),v=decodeURIComponent(kv.slice(i+1));
  if(k=='cat'||k=='lang'||k=='tema')st[k]=v?v.split('|'):[];else if(k=='p')st.p=+v||1;else if(k in st)st[k]=v})}
function writeHash(){var p=[];['q','dove','ord','y1','y2'].forEach(function(k){if(st[k]&&!(k=='dove'&&st[k]=='all')&&!(k=='ord'&&st[k]=='rel'))p.push(k+'='+encodeURIComponent(st[k]))});
 ['cat','lang','tema'].forEach(function(k){if(st[k].length)p.push(k+'='+encodeURIComponent(st[k].join('|')))});if(st.p>1)p.push('p='+st.p);
 var h='#'+p.join('&');if(h!==location.hash&&!(h=='#'&&!location.hash)){try{history.replaceState(null,'',h.length>1?h:location.pathname)}catch(e){skip=true;location.hash=h}}}
var skip=false;
function terms(q){var out=[],m,re=/"([^"]+)"|“([^”]+)”/g;while((m=re.exec(q)))out.push(fold(m[1]||m[2]).trim().replace(/\s+/g,' '));
 fold(q.replace(/"[^"]*"|“[^”]*”/g,' ')).split(/\s+/).forEach(function(w){if(w.length>1||/\d/.test(w))out.push(w)});return out.filter(Boolean)}
function loadText(){if(TX||loading)return;loading=true;status('Carico il testo completo degli articoli… (solo la prima volta, qualche secondo)');
 var NP=M.ntesti||1,got=0;function part(i){var s=document.createElement('script');s.src='assets/testi-'+i+'.js';s.onerror=fail;s.onload=function(){got++;if(got<NP){status('Carico il testo completo… '+Math.round(100*got/NP)+'%');part(i+1)}else done()};document.head.appendChild(s)}
 function fail(){status('Impossibile caricare il testo completo: la ricerca funziona solo su titoli, estratti e temi.')}
 function done(){TX=window.TESTI;FT={};var ids=Object.keys(TX),i=0;
  (function step(){var end=Math.min(ids.length,i+250);for(;i<end;i++)FT[ids[i]]=' '+fold(TX[ids[i]]).replace(/ +/g,' ')+' ';
   if(i<ids.length){status('Preparo l’indice… '+Math.round(100*i/ids.length)+'%');setTimeout(step,0)}else{FT._ok=1;run()}})()};
 part(1)}
function status(t){$('status').textContent=t||''}
function passes(r,skipF){if(skipF!='y'){if(st.y1&&r.y<st.y1)return false;if(st.y2&&r.y>st.y2)return false}
 if(skipF!='cat'&&st.cat.length&&st.cat.indexOf(r.c)<0)return false;if(skipF!='lang'&&st.lang.length&&st.lang.indexOf(r.l)<0)return false;
 if(skipF!='tema')for(var i=0;i<st.tema.length;i++)if(r.k.indexOf(st.tema[i])<0)return false;return true}
function score(r,T){if(!T.length)return 1;var s=0,full=st.dove=='all'&&FT&&FT._ok,tx=full?FT[r.id]:null;
 for(var i=0;i<T.length;i++){var w=T[i],h=0;if(r.ft.indexOf(w)>=0)h+=12;if(r.fk.indexOf(w)>=0)h+=7;if(r.fe.indexOf(w)>=0)h+=2;
  if(tx){var c=0,p=tx.indexOf(w);while(p>=0&&c<8){c++;p=tx.indexOf(w,p+w.length)}h+=c;if(tx.indexOf(' '+w)>=0)h+=1}
  if(!h)return 0;s+=h}return s}
function snippet(r,T){if(!T.length||!TX||!FT._ok||!TX[r.id]||!FT[r.id])return esc(r.e);var raw=TX[r.id],f=FT[r.id].slice(1),p=-1,w=null;
 for(var i=0;i<T.length;i++){p=f.indexOf(T[i]);if(p>=0){w=T[i];break}}if(p<0)return esc(r.e);
 var fr=fold(raw),q=fr.indexOf(w);if(q<0)return esc(r.e);var a=Math.max(0,q-110),b=Math.min(raw.length,q+190);
 while(a>0&&raw[a]!=' ')a--;var s=raw.slice(a,b),fs=fr.slice(a,b),out='',last=0,re=[];
 T.forEach(function(t){var k=fs.indexOf(t);while(k>=0){re.push([k,k+t.length]);k=fs.indexOf(t,k+t.length)}});re.sort(function(x,y){return x[0]-y[0]});
 re.forEach(function(m){if(m[0]<last)return;out+=esc(s.slice(last,m[0]))+'<mark>'+esc(s.slice(m[0],m[1]))+'</mark>';last=m[1]});out+=esc(s.slice(last));
 return(a>0?'…':'')+out+(b<raw.length?'…':'')}
function hl(t,T){var f=fold(t),re=[],out='',last=0;T.forEach(function(w){var k=f.indexOf(w);while(k>=0){re.push([k,k+w.length]);k=f.indexOf(w,k+w.length)}});
 re.sort(function(x,y){return x[0]-y[0]});re.forEach(function(m){if(m[0]<last)return;out+=esc(t.slice(last,m[0]))+'<mark>'+esc(t.slice(m[0],m[1]))+'</mark>';last=m[1]});return out+esc(t.slice(last))}
function kwlink(k){return KWS[k]?'temi/'+KWS[k]+'.html':'#tema='+encodeURIComponent(k)}
var PER=25;
function run(){writeHash();var T=terms(st.q);
 if(T.length&&st.dove=='all'&&!(FT&&FT._ok))loadText();
 var res=[],sc;for(var i=0;i<R.length;i++){var r=R[i];if(!passes(r))continue;sc=score(r,T);if(sc)res.push([sc,r])}
 if(st.ord=='new'||(!T.length&&st.ord=='rel'))res.sort(function(a,b){return a[1].d<b[1].d?1:-1});else if(st.ord=='old')res.sort(function(a,b){return a[1].d>b[1].d?1:-1});
 else res.sort(function(a,b){return b[0]-a[0]||(a[1].d<b[1].d?1:-1)});
 facets(T);$('dres').innerHTML='';
 var any=T.length||st.cat.length||st.lang.length||st.tema.length||st.y1||st.y2;
 if(!any){$('res').innerHTML='';$('pager').innerHTML='';$('active').innerHTML='';if(!loading||FT)status('Scrivi una o più parole, oppure scegli una rubrica, un periodo o un tema.');return}
 if(!loading||(FT&&FT._ok))status(res.length+(res.length==1?' testo trovato':' testi trovati')+(T.length&&st.dove=='all'&&!(FT&&FT._ok)?' (per ora solo in titoli, estratti e temi)':''));
 var np=Math.max(1,Math.ceil(res.length/PER));if(st.p>np)st.p=np;var sl=res.slice((st.p-1)*PER,st.p*PER),h='';
 sl.forEach(function(x){var r=x[1];var isd=r.c=='doc',lk=isd?r.href:'articoli/'+r.id+'.html';h+='<li class="entry'+(isd?' isdoc':'')+'"><div class="em">'+(r.d?'<time>'+hd(r.d)+'</time>':'')+(isd?'<a class="rb" href="documenti/index.html">Documento</a><span>'+esc(r.sub)+'</span>'+(r.ext?'<span class="lg">'+r.ext+'</span>':''):'<a class="rb" href="categorie/c'+r.c+'.html">'+esc(CATS[r.c]||'')+'</a>')+(r.l=='es'?'<span class="lg">ES</span>':'')+(r.w?'<span class="rt">'+Math.max(1,Math.round(r.w/220))+' min</span>':'')+'</div><h3><a href="'+lk+'">'+hl(r.t,T)+'</a></h3><p class="exc">'+snippet(r,T)+'</p><div class="chips">'+r.k.slice(0,6).map(function(k){return'<a class="chip'+(st.tema.indexOf(k)>=0?' on':'')+'" href="#" data-tema="'+esc(k)+'">'+esc(KWN[k]||k)+'</a>'}).join('')+'</div></li>'});
 $('res').innerHTML=h||'<li class="none">Nessun testo corrisponde. Prova a togliere qualche filtro o a usare meno parole.</li>';$('res').start=(st.p-1)*PER+1;
 var pg='';if(np>1){pg+=btn(st.p-1,'← Precedenti',st.p<=1);var a=Math.max(1,st.p-3),b=Math.min(np,st.p+3);if(a>1)pg+=btn(1,'1')+(a>2?'<span>…</span>':'');for(var i2=a;i2<=b;i2++)pg+=btn(i2,String(i2),false,i2==st.p);if(b<np)pg+=(b<np-1?'<span>…</span>':'')+btn(np,String(np));pg+=btn(st.p+1,'Successivi →',st.p>=np)}
 $('pager').innerHTML=pg;active()}
function btn(p,t,dis,on){return'<button '+(dis?'disabled':'')+' class="'+(on?'on':'')+'" data-p="'+p+'">'+t+'</button>'}
function cnt(skipF,T,key){var c={};for(var i=0;i<R.length;i++){var r=R[i];if(!passes(r,skipF))continue;if(T.length&&!score(r,T))continue;var v=key(r);if(v instanceof Array)v.forEach(function(x){c[x]=(c[x]||0)+1});else c[v]=(c[v]||0)+1}return c}
function facets(T){var cc=cnt('cat',T,function(r){return r.c});
 $('fcat').innerHTML=M.catorder.map(String).filter(function(c){return cc[c]||st.cat.indexOf(c)>=0}).map(function(c){return'<label class="fc"><input type="checkbox" data-f="cat" value="'+c+'"'+(st.cat.indexOf(c)>=0?' checked':'')+'> <span>'+esc(CATS[c])+'</span><small>'+(cc[c]||0)+'</small></label>'}).join('')||'<p class="hint">—</p>';
 var lc=cnt('lang',T,function(r){return r.l});$('flang').innerHTML=[['it','Italiano'],['es','Spagnolo']].map(function(l){return'<label class="fc"><input type="checkbox" data-f="lang" value="'+l[0]+'"'+(st.lang.indexOf(l[0])>=0?' checked':'')+'> <span>'+l[1]+'</span><small>'+(lc[l[0]]||0)+'</small></label>'}).join('');
 var yc=cnt('y',T,function(r){return r.y}),mx=1;YEARS.forEach(function(y){if((yc[y]||0)>mx)mx=yc[y]});
 $('fhist').innerHTML=YEARS.map(function(y){var inr=(!st.y1||y>=st.y1)&&(!st.y2||y<=st.y2);return'<a href="#" class="hb'+(inr?'':' dim')+'" data-y="'+y+'" title="'+y+': '+(yc[y]||0)+' testi"><span style="height:'+Math.max(2,Math.round(100*(yc[y]||0)/mx))+'%"></span><small>'+y.slice(2)+'</small></a>'}).join('');
 $('y1').value=st.y1;$('y2').value=st.y2;
 var tc=cnt(null,T,function(r){return r.k}),tk=Object.keys(tc).filter(function(k){return st.tema.indexOf(k)<0}).sort(function(a,b){return tc[b]-tc[a]}).slice(0,18);
 $('ftema-sel').innerHTML=st.tema.map(function(k){return'<a href="#" class="chip on" data-untema="'+esc(k)+'">'+esc(KWN[k]||k)+' ✕</a>'}).join('');
 $('ftema').innerHTML=tk.map(function(k){return'<a href="#" class="chip" data-tema="'+esc(k)+'">'+esc(KWN[k]||k)+' <small>'+tc[k]+'</small></a>'}).join('')}
function docs(T){if(!T.length||st.tema.length||st.lang.length){$('dres').innerHTML='';return}
 var out=M.docs.filter(function(d){var t=fold(d[1])+' '+d[2]+' '+fold(d[3]);return T.every(function(w){return t.indexOf(w)>=0})});
 if(!out.length){$('dres').innerHTML='';return}
 $('dres').innerHTML='<div class="box dbox"><h4>Documenti scaricabili ('+out.length+')</h4><ul class="mini-list">'+out.slice(0,12).map(function(d){return'<li>'+(d[4]?'<a href="'+esc(d[4])+'">'+hl(d[1],T)+'</a>':'<a href="documenti/cat'+d[5]+'.html#d'+d[0]+'">'+hl(d[1],T)+'</a> <small>(non recuperato)</small>')+'<time>'+esc(d[3])+'</time></li>'}).join('')+'</ul>'+(out.length>12?'<p class="hint">…e altri '+(out.length-12)+'. Restringi la ricerca per vederli.</p>':'')+'</div>'}
function active(){var a=[];if(st.q)a.push(['q','“'+st.q+'”']);st.cat.forEach(function(c){a.push(['cat:'+c,CATS[c]])});st.lang.forEach(function(l){a.push(['lang:'+l,l=='es'?'Spagnolo':'Italiano'])});
 st.tema.forEach(function(k){a.push(['tema:'+k,'#'+(KWN[k]||k)])});if(st.y1||st.y2)a.push(['y',(st.y1||YEARS[0])+'–'+(st.y2||YEARS[YEARS.length-1])]);
 $('active').innerHTML=a.length?a.map(function(x){return'<a href="#" class="chip on" data-rm="'+esc(x[0])+'">'+esc(x[1])+' ✕</a>'}).join(''):''}
window.S={run:function(){st.q=$('q').value.trim();st.p=1;run()},reset:function(){var q=st.q;st={q:q,dove:st.dove,ord:st.ord,y1:'',y2:'',cat:[],lang:[],tema:[],p:1};run()}};
var opts='<option value="">—</option>'+YEARS.map(function(y){return'<option>'+y+'</option>'}).join('');$('y1').innerHTML=opts;$('y2').innerHTML=opts;
$('tdl').innerHTML=Object.keys(KWN).sort().map(function(k){return'<option value="'+esc(KWN[k])+'">'}).join('');
var TBYNAME={};Object.keys(KWN).forEach(function(k){TBYNAME[fold(KWN[k]).trim()]=k});
$('tq').addEventListener('change',function(){var k=TBYNAME[fold(this.value).trim()];if(k&&st.tema.indexOf(k)<0){st.tema.push(k);st.p=1;run()}this.value=''});
var tmr;$('q').addEventListener('input',function(){clearTimeout(tmr);tmr=setTimeout(function(){S.run()},300)});
document.querySelectorAll('input[name=dove]').forEach(function(r){r.addEventListener('change',function(){st.dove=this.value;st.p=1;run()})});
$('ord').addEventListener('change',function(){st.ord=this.value;st.p=1;run()});
$('y1').addEventListener('change',function(){st.y1=this.value;if(st.y2&&st.y1>st.y2)st.y2=st.y1;st.p=1;run()});
$('y2').addEventListener('change',function(){st.y2=this.value;if(st.y1&&st.y2<st.y1)st.y1=st.y2;st.p=1;run()});
document.addEventListener('change',function(e){var f=e.target.getAttribute&&e.target.getAttribute('data-f');if(!f)return;var v=e.target.value,a=st[f],i=a.indexOf(v);if(e.target.checked&&i<0)a.push(v);if(!e.target.checked&&i>=0)a.splice(i,1);st.p=1;run()});
document.addEventListener('click',function(e){var t=e.target.closest('[data-tema],[data-untema],[data-rm],[data-p],[data-y]');if(!t)return;e.preventDefault();
 if(t.hasAttribute('data-tema')){var k=t.getAttribute('data-tema');if(st.tema.indexOf(k)<0)st.tema.push(k)}
 else if(t.hasAttribute('data-untema')){st.tema.splice(st.tema.indexOf(t.getAttribute('data-untema')),1)}
 else if(t.hasAttribute('data-p')){if(t.disabled)return;st.p=+t.getAttribute('data-p');run();$('q').scrollIntoView({behavior:'smooth'});return}
 else if(t.hasAttribute('data-y')){var y=t.getAttribute('data-y');if(st.y1==y&&st.y2==y){st.y1='';st.y2=''}else{st.y1=y;st.y2=y}}
 else{var r=t.getAttribute('data-rm');if(r=='q'){st.q='';$('q').value=''}else if(r=='y'){st.y1='';st.y2=''}else{var p=r.split(':'),f=p.shift(),v=p.join(':');st[f].splice(st[f].indexOf(v),1)}}
 st.p=1;run()});
function fromHash(){readHash();$('q').value=st.q;document.querySelector('input[name=dove][value='+(st.dove=='tit'?'tit':'all')+']').checked=true;$('ord').value=st.ord;run()}
window.addEventListener('hashchange',function(){if(skip){skip=false;return}fromHash()});
fromHash();
})();
