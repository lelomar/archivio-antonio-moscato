import os,re,json,sys,math,collections,html,unicodedata
WORK=os.environ.get('MOSCATO_WORK',os.path.dirname(os.path.abspath(__file__)))
_src=open(os.path.join(WORK,'build.py')).read()
exec(compile(_src[:_src.index('def li(')],'build_base','exec'))
from bs4 import BeautifulSoup
# pagine di servizio del vecchio sito e articoli pubblicati due volte
DROP_ART={67:'index.html',273:'index.html',272:'index.html',25:'index.html',235:'cerca.html',119:'index.html'}
DUP_ART={1946:1947,2033:2034,2040:2041,2264:2263,2020:2021,2279:2280}
ART_REDIR.update(DUP_ART)
arts=[a for a in arts if a['id'] not in DROP_ART and a['id'] not in DUP_ART]
A={a['id']:a for a in arts}
def slugify(t):
    t=unicodedata.normalize('NFKD',t.lower()); t=''.join(c for c in t if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]+','-',t).strip('-')[:60] or 'x'
os.makedirs(os.path.join(OUT,'temi'),exist_ok=True)
BASEKW={x.strip() for x in 'movimento operaio, anticapitalismo, antistalinismo, democrazia operaia, internazionalismo, rivoluzione,cuba, che guevara, america latina, sinistra critica'.split(',')}
BASEKW={norm(x) for x in BASEKW}
# home default keywords must be ignored only when they are exactly the site default set
DEFAULTSET=norm('movimento operaio, anticapitalismo, antistalinismo, democrazia operaia, internazionalismo, rivoluzione,Cuba, Che Guevara, America Latina, Sinistra Critica')
kwdisp=collections.defaultdict(collections.Counter)
_TA=json.load(open(os.path.join(WORK,'temi_alias.json')))
ALIAS=_TA['alias']; DISP=_TA['display']
_TCF=os.path.join(WORK,'temi_classificazione.json'); _TC=json.load(open(_TCF,encoding='utf-8')) if os.path.exists(_TCF) else {}
_LAB2K={v:k for k,v in DISP.items()}
def _lk(l): return _LAB2K.get(l) or norm(l)
for _s,_t in _TC.get('unisci',{}).items(): ALIAS[norm(_s)]=_lk(_t)
for _s,_t in _TC.get('dividi',{}).items(): ALIAS[norm(_s)]=[_lk(x) for x in _t]
for _s,_t in _TC.get('visualizza',{}).items(): DISP[_lk(_s)]=_t
for _t in {x for v in _TC.get('dividi',{}).values() for x in v}: DISP.setdefault(_lk(_t),_t)
def _risolvi(k,seen=()):
    t=ALIAS.get(k,k)
    if isinstance(t,list): return [y for x in t for y in _risolvi(x,seen+(k,))]
    if t==k or t in seen: return [t]
    return _risolvi(t,seen+(k,))
_GENERICHE=('movimento operaio','anticapitalismo','antistalinismo','democrazia operaia','internazionalismo','rivoluzione')
ORIGKW=[]  # (id articolo, posizione, forma originale, trattamento, [chiavi dei temi])
ES=set('el la los las que de y en por para con una del al es se como pero sus su muy fue han esta este entre sobre tambien gobierno'.split())
IT=set('il lo la gli le che di e in per con una del al è si come ma suoi suo molto fu hanno questa questo tra sulla anche governo non'.split())
DCONV=os.path.join(WORK,'dconv')
os.makedirs(os.path.join(OUT,'documenti','testo'),exist_ok=True)
def ddate(s):
    m=re.match(r'(\d{2})/(\d{2})/(\d{4})',s or '');return f'{m.group(3)}-{m.group(2)}-{m.group(1)}' if m else ''
for g,d in docs.items():
    d['iso']=ddate(d.get('date')); d['text']=''; d['page']=None
    if not d.get('out'): continue
    d['broken']=d.get('size')==1048576
    base=os.path.splitext(os.path.basename(d['out']))[0]; ext=d['out'].rsplit('.',1)[-1].lower()
    body=''
    if ext=='pdf':
        p=os.path.join(DCONV,'txt',base+'.txt')
        if os.path.exists(p):
            raw=open(p,encoding='utf-8',errors='ignore').read().replace('\f','\n\n')
            paras=[re.sub(r'-\n(?=[a-zà-ù])','',x) for x in re.split(r'\n\s*\n',raw)]
            paras=[re.sub(r'\s*\n\s*',' ',x).strip() for x in paras]
            body=''.join(f'<p>{esc(x)}</p>' for x in paras if x)
    else:
        p=os.path.join(DCONV,'html',base+'.html')
        if os.path.exists(p):
            s=open(p,encoding='utf-8',errors='ignore').read()
            sb=BeautifulSoup(s,'lxml')
            bd=sb.body
            if bd:
                for t in bd.find_all(['title','meta']): t.decompose()
                body=clean(bd.decode_contents(),'../../')
    txt=re.sub(r'\s+',' ',BeautifulSoup(body,'lxml').get_text(' ')).strip() if body else ''
    if len(txt.split())<20: continue
    d['text']=txt; d['_body']=body; d['words']=len(txt.split()); d['page']=f'documenti/testo/{g}.html'
    w=norm(txt).split()[:800]; es=sum(1 for x in w if x in ES); it=sum(1 for x in w if x in IT)
    d['lang']='es' if es>it*1.2 else 'it'
print('doc texts',sum(1 for d in docs.values() if d.get('page')),flush=True)
for a in arts:
    raw=a.get('kw') or ''
    ks=[]; _def=norm(raw)==DEFAULTSET
    for _i,x in enumerate([y.strip() for y in raw.split(',')]):
        if not x: continue
        k=norm(x)
        if _def: ORIGKW.append((a['id'],_i+1,x,'esclusa: è l’elenco predefinito del sito, non scelto per l’articolo',[])); continue
        if not k: ORIGKW.append((a['id'],_i+1,x,'esclusa: senza lettere',[])); continue
        if k in _GENERICHE: ORIGKW.append((a['id'],_i+1,x,'esclusa: comune a quasi tutto il sito',[])); continue
        tg=list(dict.fromkeys(_risolvi(k)))
        ORIGKW.append((a['id'],_i+1,x,'tema' if tg==[k] else ('divisa in più temi' if len(tg)>1 else 'unificata con un’altra forma'),tg))
        for t in tg:
            if t not in ks: ks.append(t)
            if len(tg)==1: kwdisp[t][x]+=1
    a['kws']=ks
    a['body']=clean(a['html'],'../')
    txt=BeautifulSoup(a['body'],'lxml').get_text(' ')
    txt=re.sub(r'\s+',' ',txt).strip()
    a['plain']=txt
    w=norm(txt).split(); a['words']=len(w)
    es=sum(1 for x in w[:600] if x in ES); it=sum(1 for x in w[:600] if x in IT)
    a['lang']='es' if es>it*1.2 else 'it'
    t=txt
    if t.lower().startswith(a['title'].lower()[:30]): t=t[len(a['title']):].strip(' .:-')
    a['exc']=(t[:240].rsplit(' ',1)[0]+'…') if len(t)>240 else t
KWN={k:c.most_common(1)[0][0] for k,c in kwdisp.items()}
def kwname(k):
    if k in DISP: return DISP[k]
    n=KWN.get(k,k); return n[:1].upper()+n[1:] if n.islower() else n
kwcount=collections.Counter(k for a in arts for k in a['kws'])
KWSLUG={k:slugify(k) for k in kwcount}
_spec_v=__import__('importlib.util').util.spec_from_file_location('vocabolario',os.path.join(WORK,'vocabolario.py')); _VOC=__import__('importlib.util').util.module_from_spec(_spec_v); _spec_v.loader.exec_module(_VOC)
TIPO,AMBT=_VOC.classifica(_TC,kwcount,_lk,_risolvi)
_IDF=os.path.join(WORK,'temi_identificativi.json'); IDENT=json.load(open(_IDF)) if os.path.exists(_IDF) else {}
FORME=collections.defaultdict(collections.Counter)
for _o in ORIGKW:
    for _k in _o[4]: FORME[_k][_o[2]]+=1
ORIG_ART=collections.defaultdict(list)
for _o in ORIGKW: ORIG_ART[str(_o[0])].append(_o)
N=len(arts); inv=collections.defaultdict(list)
for a in arts:
    for k in a['kws']: inv[k].append(a)
for a in arts:
    sc=collections.Counter()
    for k in a['kws']:
        if kwcount[k]>400: continue
        idf=math.log(N/kwcount[k])
        for b in inv[k]:
            if b is not a: sc[b['id']]+=idf
    for bid in list(sc):
        b=A[bid]
        if b['catid']==a['catid']: sc[bid]+=0.3
        if a['date'] and b['date']:
            dy=abs(int(a['date'][:4])-int(b['date'][:4])); sc[bid]-=0.15*dy
    a['rel']=[i for i,_ in sc.most_common(6) if _>1.0][:6]
print('prep ok',N,'kw',len(kwcount),'es',sum(1 for a in arts if a['lang']=='es'),flush=True)
NAV=[('index.html','Home'),('attualita.html','Rubriche'),('temi.html','Temi'),('autori.html','Autori'),('documenti/index.html','I grandi nodi del Novecento'),('anni.html','Cronologia'),('accadde-oggi.html','Accadde oggi'),('cerca.html','Ricerca')]
def page(title,content,pre,active='',body_cls='',lang='it'):
    nav=''.join(f'<a href="{pre}{h}"{" class=on aria-current=page" if h==active else ""}>{esc(t)}</a>' for h,t in NAV)
    return f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} · Movimento operaio, il sito di Antonio Moscato ricostruito</title><link rel="stylesheet" href="{pre}assets/stile.css"><script src="{pre}assets/sito.js"></script></head>
<body class="{body_cls}" data-pre="{pre}"><a class="skip" href="#contenuto">Salta al contenuto</a><div id="prog" aria-hidden="true"></div><div class="credit"><div class="wrap"><a href="{pre}progetto.html">Il progetto di recupero</a> a cura di <a href="https://lelomar.substack.com" target="_blank" rel="noopener">Leonardo Lomartire · lelomar.substack.com</a></div></div><header class="top"><div class="wrap bar"><a class="brand" href="{pre}index.html"><span class="k">Movimento operaio</span><span class="s">Il sito di Antonio Moscato, ricostruito</span></a>
<form class="mini" role="search" onsubmit="return miniCerca(this)"><input name="q" type="search" placeholder="Cerca nell’archivio…" aria-label="Cerca"><button aria-label="Cerca">⌕</button></form><button class="hamb" type="button" aria-expanded="false" aria-controls="menu"><span class="hl" aria-hidden="true"></span>Menu</button></div>
<div class="wrap"><nav class="mainnav" id="menu" aria-label="Menu principale">{nav}</nav></div></header><main class="wrap" id="contenuto" tabindex="-1">{content}</main>
<footer class="foot"><div class="wrap"><p><b>Movimento operaio. Il sito di Antonio Moscato (2009–2021), ricostruito</b>. Versione statica, consultabile offline, del sito <em>antoniomoscato.altervista.org</em> (2009–2021), ricavata dalle copie conservate dall’Internet Archive. <a href="{pre}criteri.html">Criteri di edizione</a>. Codice libero (GPL-3.0) su <a href="https://github.com/lelomar/archivio-antonio-moscato" target="_blank" rel="noopener">GitHub</a>. Recupero, ricostruzione e cura di <a href="https://lelomar.substack.com" target="_blank" rel="noopener">Leonardo Lomartire</a>.</p><p>I link segnati con ↗ portano a siti esterni o a pagine non recuperate e richiedono una connessione.</p></div></footer>
</body></html>'''
def chips(ks,pre,n=8):
    return ''.join(f'<a class="chip" href="{pre}temi/{KWSLUG[k]}.html">{esc(kwname(k))}</a>' if kwcount[k]>=3 else f'<a class="chip" href="{pre}cerca.html#tema={urllib.parse.quote(k)}">{esc(kwname(k))}</a>' for k in ks[:n])
def entry(a,pre,showcat=True,exc=True):
    c=f'<a class="rb" href="{pre}categorie/c{a["catid"]}.html">{esc(catname(a["catid"]))}</a>' if showcat else ''
    e=f'<p class="exc">{esc(a["exc"])}</p>' if exc and a['exc'] else ''
    lg='<span class="lg">ES</span>' if a['lang']=='es' else ''
    return f'''<li class="entry" data-t="{esc(norm(a['title']+' '+' '.join(a['kws'])))}"><div class="em"><time>{hdate(a['date'])}</time>{c}{lg}</div><h3><a href="{pre}articoli/{a['id']}.html">{esc(a['title'])}</a></h3>{e}<div class="chips">{chips(a['kws'],pre,5)}</div></li>'''
def entries_by_year(items,pre,showcat=False):
    g=collections.OrderedDict()
    for a in items: g.setdefault(a['date'][:4] or 's.d.',[]).append(a)
    jump='<nav class="jump" aria-label="Vai all’anno">'+''.join(f'<a href="#y{y}">{y}<small>{len(l)}</small></a>' for y,l in g.items())+'</nav>'
    body=''.join(f'<section class="ygroup" id="y{y}"><h2 class="yr">{y} <small>{len(l)} testi</small></h2><ul class="entries">{"".join(entry(a,pre,showcat) for a in l)}</ul></section>' for y,l in g.items())
    filt='<div class="filt"><input type="search" placeholder="Filtra per titolo o tema…" oninput="filtra(this.value)" aria-label="Filtra"><span id="fcount"></span></div>'
    return filt+jump+body
def rtime(w):
    m=max(1,round(w/220)); return f'{m} min di lettura'
bycat=collections.defaultdict(list)
for a in arts: bycat[a['catid']].append(a)
# --- autori: proposte automatiche + correzioni verificate ---
import urllib.parse as _up
_AUT={r['id']:r for r in json.load(open(os.path.join(WORK,'autori_proposte.json')))}
_COR=json.load(open(os.path.join(WORK,'autori_correzioni.json'))) if os.path.exists(os.path.join(WORK,'autori_correzioni.json')) else {}
for _k,_v in _COR.items():
    if _k in _AUT: _AUT[_k].update(_v); _AUT[_k]['certezza']='verificata'
for a in arts:
    r=_AUT.get(str(a['id']),{}); a['autore']=r.get('autore') or ''; a['cert']=r.get('certezza','presunta'); a['mosc']=r.get('moscato','')
_DS=json.load(open(os.path.join(WORK,'date_scrittura.json'))) if os.path.exists(os.path.join(WORK,'date_scrittura.json')) else {}
_DC=json.load(open(os.path.join(WORK,'date_correzioni.json'))) if os.path.exists(os.path.join(WORK,'date_correzioni.json')) else {}
_DS.update(_DC)
for a in arts:
    d=_DS.get(str(a['id'])); a['scritto']=d['etichetta'] if d else ''; a['scritto_ind']=d.get('indizio','') if d else ''
GH='https://github.com/lelomar/archivio-antonio-moscato/issues/new'
MAILTO='lelomar@gmail.com'
def segnala(a,url):
    gh=GH+'?'+_up.urlencode({'template':'3-autore.yml','title':'[Autore] '+a['title'][:80],'articolo':url,'autore_attuale':a['autore'] or 'non indicato','labels':'autore'},quote_via=_up.quote)
    ml='mailto:'+MAILTO+'?subject='+_up.quote('correzione proposta progetto moscato')+'&body='+_up.quote('Articolo: '+url+'\n\n')
    return f'<aside class="segnala"><p><b>Sai qualcosa in più su questo testo?</b> Un autore da correggere, una data, un errore: segnalalo.</p><p class="sg-l"><a class="btn" href="{gh}" target="_blank" rel="noopener">Segnala su GitHub</a><a class="btn alt" href="{ml}">Scrivi una email</a></p></aside>'
def byline(a):
    if not a['autore']: return '<p class="byline">Autore da identificare <span class="cert c-bassa">da verificare</span></p>'
    lab={'media':'<span class="cert c-media">attribuzione da verificare</span>','presunta':'<span class="cert c-pres">attribuzione presunta</span>','bassa':'<span class="cert c-media">da verificare</span>'}.get(a['cert'],'')
    m=f' <span class="mosc">· con {esc(a["mosc"].replace(" di Antonio Moscato",""))} di Antonio Moscato</span>' if a['mosc'] and a['autore']!='Antonio Moscato' else ''
    return f'<p class="byline">di <b>{esc(a["autore"])}</b>{m} {lab}</p>'
import importlib.util as _iu2
_cs=_iu2.spec_from_file_location('catalogo_p',os.path.join(WORK,'catalogo.py')); _cp=_iu2.module_from_spec(_cs); _cs.loader.exec_module(_cp)
_PROV=_cp.provenienza(root,WORK,arts)
_MESI='gennaio febbraio marzo aprile maggio giugno luglio agosto settembre ottobre novembre dicembre'.split()
def _tsd(ts): return f"{int(ts[6:8])} {_MESI[int(ts[4:6])-1]} {ts[:4]}" if len(ts)>=8 else ''
def _apa_name(n):
    p=n.split(); return (p[-1]+', '+'. '.join(x[0] for x in p[:-1])+'.') if len(p)>1 else n
_LWB=json.load(open(os.path.join(WORK,'link_wayback.json'))) if os.path.exists(os.path.join(WORK,'link_wayback.json')) else {}
_VER=json.load(open(os.path.join(OUT,'.zenodo.json'))).get('version','') if os.path.exists(os.path.join(OUT,'.zenodo.json')) else ''
_DUPIN={}
for _k,_v in DUP_ART.items(): _DUPIN.setdefault(str(_v),[]).append(str(_k))
def _interventi(a):
    b=a['body']; c=collections.Counter()
    for h in re.findall(r'<a\s[^>]*href="([^"]+)"',b):
        h=html.unescape(h)
        if re.match(r'(\.\./)+(articoli|categorie|documenti|temi|anni|cerca)',h): c['int']+=1
        elif 'web.archive.org/web/' in h and 'antoniomoscato' in h: c['wbi']+=1
        elif re.match(r'https?://',h) and 'archive.org' not in h and 'antoniomoscato' not in h:
            st=(_LWB.get(h.strip()) or {}).get('stato')
            if st=='archiviato': c['ea']+=1
            elif st=='non archiviato': c['en']+=1
        elif h.startswith('#'): c['note']+=1
    c['img']=len(re.findall(r'<img[^>]+src="(\.\./)+assets/img/',b))
    out=['pulizia del codice della pagina (menu, script, pulsanti di condivisione, stili di Word): il testo non è stato modificato']
    def pl(n,s1,s2): return f'{n} {s1 if n==1 else s2}'
    if c['int']: out.append(pl(c['int'],'collegamento al vecchio sito ricondotto','collegamenti al vecchio sito ricondotti')+' alle pagine di questo archivio')
    if c['wbi']: out.append(pl(c['wbi'],'collegamento','collegamenti')+' a pagine non conservate, indirizzat'+('o' if c['wbi']==1 else 'i')+' alla Wayback Machine (↗)')
    if c['ea']: out.append(pl(c['ea'],'link esterno indirizzato','link esterni indirizzati')+' alla copia d’archivio dell’epoca, con l’indirizzo originale accanto («orig.»)')
    if c['en']: out.append(pl(c['en'],'link esterno senza copia d’archivio, segnato','link esterni senza copia d’archivio, segnati')+' «non archiviato»')
    if c['img']: out.append(pl(c['img'],'immagine recuperata','immagini recuperate')+' e inclusa'+('' if c['img']==1 else '')+' nell’archivio')
    if c['note']: out.append(pl(c['note'],'rimando interno','rimandi interni')+' (note, indici) res'+('o' if c['note']==1 else 'i')+' funzionant'+('e' if c['note']==1 else 'i'))
    cert=a.get('cert','')
    out.append('autore '+({'verificata':'confermato da una segnalazione','alta':'ricavato da una firma nel testo','media':'proposto dal programma, da verificare','bassa':'proposto dal programma, da verificare','presunta':'presunto: nessuna firma, testo pubblicato sul sito di Moscato'}.get(cert,'da verificare')))
    if a.get('scritto'): out.append('data di scrittura ricavata dal testo')
    for d in _DUPIN.get(str(a['id']),[]): out.append(f'unito il doppione AM-{d}, pubblicato due volte')
    return out
def scheda(a,url):
    u,ts=_PROV.get(str(a['id']),('',''))
    wb=('https://web.archive.org/web/'+ts+'/'+u) if ts else ''
    aut=a['autore'] or 'Autore non identificato'
    d=hdate(a['date']) if a['date'] else 's.d.'
    cit=(f"{esc(aut)}, «{esc(a['title'])}», in <em>Movimento operaio – La pagina di Antonio Moscato</em>, {d}; ora in <em>Movimento operaio. Il sito di Antonio Moscato (2009–2021), ricostruito</em>, a cura di Leonardo Lomartire, 2026, {url} (consultato il <span class=\"oggi\">…</span>). DOI: 10.5281/zenodo.23670900.")
    ya=a['date'][:4] if a['date'] else 's.d.'
    _an=' & '.join(_apa_name(x) for x in re.split(r'\s+e\s+',aut)); _gm=(', '+str(int(a['date'][8:10]))+' '+_MESI[int(a['date'][5:7])-1]) if a['date'] else ''
    apa=(f"{esc(_an)} ({ya}{_gm}). <em>{esc(a['title'])}</em>. In L. Lomartire (a cura di), <em>Movimento operaio. Il sito di Antonio Moscato (2009–2021), ricostruito</em>. Zenodo. https://doi.org/10.5281/zenodo.23670900 · {url}")
    rows=[('Identificativo',f'AM-{a["id"]}'),('Autore',esc(aut)+(f' <span class="d">({esc(a["mosc"])})</span>' if a['mosc'] and a['autore']!='Antonio Moscato' else '')+(f' <span class="d">· attribuzione {"presunta" if a["cert"]=="presunta" else "da verificare"}</span>' if a['cert'] in ('presunta','media','bassa') else '')),
          ('Pubblicato sul sito',d)]
    if a.get('scritto'): rows.append(('Data di scrittura',esc(a['scritto'])+' <span class="d">(secondo il testo)</span>'))
    _ok=ORIG_ART.get(str(a['id']),[])
    if _ok:
        _esc=[o for o in _ok if not o[4]]
        rows.append(('Parole chiave originali',', '.join(f'«{esc(o[2])}»' for o in _ok)+(' <span class="d">(elenco predefinito del sito, non usato per i temi)</span>' if _esc and len(_esc)==len(_ok) and 'predefinito' in _esc[0][3] else '')))
    dl=''.join(f'<dt>{k}</dt><dd>{v}</dd>' for k,v in rows)
    _id='AM-'+str(a['id']); _nw=f"{len((a.get('plain') or '').split()):,}".replace(',','.')
    _iv=''.join(f'<li>{esc(x)}</li>' for x in _interventi(a))
    _cop=f'<a href="{esc(wb)}" target="_blank" rel="noopener">Wayback Machine, {_tsd(ts)}</a>' if wb else 'copia non identificata'
    liv=(f'<li><b>Originale</b> <span class="lid">{_id}.o</span><span class="ld">Pubblicato sul sito antoniomoscato.altervista.org il {d}. <span class="u">{esc(u)}</span></span></li>'
         f'<li><b>Cattura</b> <span class="lid">{_id}.c</span><span class="ld">La copia da cui viene il testo: {_cop}.</span></li>'
         f'<li><b>Testo estratto</b> <span class="lid">{_id}.t</span><span class="ld">Il corpo dell’articolo, estratto dalla copia senza modificarne le parole: {_nw} parole.</span></li>'
         f'<li><b>Edizione</b> <span class="lid">{_id}.e</span><span class="ld">Questa pagina, nella versione {_VER} dell’archivio.</span></li>'
         f'<li><b>Interventi</b><span class="ld"><ul>{_iv}</ul></span></li>')
    return f'''<section class="scheda" aria-labelledby="sch-{a['id']}"><h2 id="sch-{a['id']}">Scheda d’archivio</h2><dl>{dl}</dl>
<h3>Dal sito originale a questa pagina</h3><ol class="livelli">{liv}</ol>
<p class="hint">Ogni livello ha un identificativo, un’impronta SHA-256 e il legame con quello da cui deriva nei <a href="../dati/provenienza.csv">dati di provenienza</a>; le regole seguite sono nei <a href="../criteri.html">criteri di edizione</a>, il modello è spiegato nella <a href="https://github.com/lelomar/archivio-antonio-moscato/blob/main/dati/MODELLO.md" target="_blank" rel="noopener">guida ai dati</a>.</p>
<h3>Come citare</h3><p class="cit" id="cit1-{a['id']}">{cit}</p><button type="button" class="cpy" data-copy-from="#cit1-{a['id']}">Copia la citazione</button>
<p class="cit apa" id="cit2-{a['id']}"><span class="d">APA</span> {apa}</p><button type="button" class="cpy" data-copy-from="#cit2-{a['id']}">Copia in formato APA</button></section>'''
for c in bycat: bycat[c].sort(key=sortkey,reverse=True)
for a in arts:
    pre='../'; lst=bycat[a['catid']]; i=lst.index(a)
    prev=lst[i+1] if i+1<len(lst) else None; nxt=lst[i-1] if i>0 else None
    pn=(f'<a class="pn" href="{nxt["id"]}.html"><small>← più recente</small>{esc(nxt["title"])}</a>' if nxt else '<span></span>')
    pn+=(f'<a class="pn r" href="{prev["id"]}.html"><small>precedente →</small>{esc(prev["title"])}</a>' if prev else '<span></span>')
    crumb=('<a href="../attualita.html">Rubriche</a> › ')+f'<a href="../categorie/c{a["catid"]}.html">{esc(catname(a["catid"]))}</a>'
    orig=WB+('http://antoniomoscato.altervista.org/index.php?option=com_content&view=article&id=%s'%a['id'] if isinstance(a['id'],int) else 'https://antoniomoscato.altervista.org/'+a.get('slug','')+'/')
    rel=''.join(f'<li><a href="{r}.html">{esc(A[r]["title"])}</a><time>{hdate(A[r]["date"])}</time></li>' for r in a['rel'])
    same=''.join(f'<li><a href="{b["id"]}.html">{esc(b["title"])}</a><time>{hdate(b["date"])}</time></li>' for b in lst[max(0,i-2):i+3] if b is not a)
    yr=a['date'][:4]
    aside=f'''<aside class="side"><div class="box"><h4>Questo testo</h4><p><a href="../categorie/c{a['catid']}.html">{esc(catname(a['catid']))}</a><br>{hdate(a['date'])}{f' · <a href="../anni/{yr}.html">tutto il {yr}</a>' if yr else ''}<br>{rtime(a['words'])}</p>
<div class="tools"><button type="button" onclick="fs(-1)" title="Testo più piccolo" aria-label="Riduci il testo">A−</button><button type="button" onclick="fs(1)" title="Testo più grande" aria-label="Ingrandisci il testo">A+</button><button type="button" onclick="window.print()">Stampa</button></div></div>
{f'<div class="box"><h4>Temi</h4><div class="chips">{chips(a["kws"],pre,14)}</div></div>' if a['kws'] else ''}
{f'<div class="box"><h4>Testi correlati</h4><ul class="mini-list">{rel}</ul></div>' if rel else ''}
<div class="box"><h4>Nella stessa rubrica</h4><ul class="mini-list">{same}</ul></div></aside>'''
    content=f'''<div class="artgrid"><article class="art"><p class="crumb">{crumb}</p><h1>{esc(a["title"])}</h1>
{byline(a)}<p class="meta">{('pubblicato sul sito il <time datetime="'+a['date']+'">'+hdate(a['date'])+'</time>') if a['date'] else 'data di pubblicazione non nota'}{(' · <span class="scritto" title="'+esc(a['scritto_ind'])+'">'+esc(a['scritto'])+', secondo il testo</span>') if a['scritto'] else ''} · {rtime(a['words'])}{' · testo in spagnolo' if a['lang']=='es' else ''}</p>
<div class="testo" id="testo">{a['body']}</div>{scheda(a,'https://lelomar.github.io/archivio-antonio-moscato/articoli/'+str(a['id'])+'.html')}{segnala(a,'https://lelomar.github.io/archivio-antonio-moscato/articoli/'+str(a['id'])+'.html')}<p class="orig"><a href="{orig}" target="_blank" rel="noopener">Pagina originale sulla Wayback Machine ↗</a></p>
<nav class="pnav">{pn}</nav></article>{aside}</div>'''
    open(os.path.join(OUT,'articoli',f'{a["id"]}.html'),'w').write(page(a['title'],content,pre,'','pg-art',a['lang']))
print('articles written',flush=True)
cat_order=[c for c in SEC_CATS if c in bycat]+[-1]+[c for c in bycat if c not in SEC_CATS and c!=-1]
CATDESC={28:'I commenti scritti a ridosso degli avvenimenti: la cronaca politica italiana e internazionale letta da sinistra.',20:'Le omissioni, i doppi standard e le rimozioni della politica e dell’informazione.',57:'Guerre, interventi e rivalità tra potenze.',6:'Il bilancio storico dell’URSS e dei paesi del “socialismo reale”, e le nostalgie che ha lasciato.',7:'Israele, Palestina, le rivolte arabe e la regione.',8:'Cuba, il Venezuela, il Brasile e le sinistre latinoamericane.',32:'Note ed editoriali in spagnolo, soprattutto di Guillermo Almeyra.',52:'Le newsletter inviate agli iscritti.',-1:'I testi dell’ultima fase del sito, sulla piattaforma WordPress.'}
def span(c):
    ys=[a['date'][:4] for a in bycat[c] if a['date']]; return f'{min(ys)}–{max(ys)}' if ys else ''
for c in cat_order:
    if c not in bycat: continue
    _yc=collections.Counter(a['date'][:4] for a in bycat[c] if a['date'] and '2009'<=a['date'][:4]<='2021'); _mx=max(_yc.values()) if _yc else 1
    _bars=''.join(f'<a class="rb-y{" z" if not _yc.get(str(y)) else ""}" href="#y{y}" title="{y}: {_yc.get(str(y),0)} testi"><span style="height:{max(2,round(100*_yc.get(str(y),0)/_mx))}%"></span><small>{str(y)[2:]}</small></a>' for y in range(2009,2022))
    content=f'<p class="crumb"><a href="../attualita.html">Rubriche</a></p><header class="rhead"><h1>{esc(catname(c))}</h1><p class="lead">{esc(CATDESC.get(c,""))}</p><div class="rh-row"><p class="rh-n"><b>{len(bycat[c])}</b> testi<br>{span(c)}</p><div class="rh-h" aria-label="Testi per anno">{_bars}</div></div></header>'+entries_by_year(bycat[c],'../')
    open(os.path.join(OUT,'categorie',f'c{c}.html'),'w').write(page(catname(c),content,'../','attualita.html'))
def rcard(c,pre=''):
    last=''.join(f'<li><a href="{pre}articoli/{a["id"]}.html">{esc(a["title"])}</a></li>' for a in bycat[c][:3])
    return f'<div class="rcard"><h3><a href="{pre}categorie/c{c}.html">{esc(catname(c))}</a></h3><p class="meta">{len(bycat[c])} testi · {span(c)}</p><p class="rd">{esc(CATDESC.get(c,""))}</p><ul>{last}</ul><a class="more" href="{pre}categorie/c{c}.html">Tutta la rubrica →</a></div>'
main_c=[c for c in cat_order if c in bycat and (c in SEC_CATS or c==-1)]
others=''.join(f'<li><a href="categorie/c{c}.html">{esc(catname(c))}</a> <span class="d">{len(bycat[c])} testi</span></li>' for c in cat_order if c in bycat and c not in main_c)
open(os.path.join(OUT,'attualita.html'),'w').write(page('Rubriche',f'<header class="phead"><h1>Le rubriche</h1><p class="lead">Articoli, commenti a caldo e polemiche, nelle rubriche in cui il sito era organizzato.</p></header><div class="rgrid">{"".join(rcard(c) for c in main_c)}</div><h2 class="sec">Altre pagine</h2><ul class="plain">{others}</ul>','','attualita.html'))
years=collections.defaultdict(list)
for a in arts: years[a['date'][:4] or 's.d.'].append(a)
ys=sorted([y for y in years if y!='s.d.' and '2009'<=y<='2021'])
mx=max(len(years[y]) for y in ys)
def histo(pre='',big=False):
    bars=''.join(f'<a class="hb" href="{pre}anni/{y}.html" title="{y}: {len(years[y])} testi" aria-label="{y}: {len(years[y])} testi"><span style="height:{max(3,round(100*len(years[y])/mx))}%"></span><small>{y[2:] if not big else y}</small></a>' for y in ys)
    return f'<div class="histo{" big" if big else ""}" role="group" aria-label="Testi pubblicati per anno">{bars}</div>'
open(os.path.join(OUT,'anni.html'),'w').write(page('Cronologia',f'<header class="phead"><h1>Cronologia</h1><p class="lead">Tutti i testi anno per anno. Clicca su una colonna per aprire l’anno.</p></header>{histo("",True)}<div class="ycards">'+''.join(f'<a class="ycard" href="anni/{y}.html"><b>{y}</b><span>{len(years[y])} testi</span></a>' for y in sorted(years,reverse=True))+'</div>','','anni.html'))
for y,l in years.items():
    l.sort(key=sortkey,reverse=True)
    g=collections.OrderedDict()
    for a in l: g.setdefault(a['date'][5:7],[]).append(a)
    jump='<nav class="jump">'+''.join(f'<a href="#m{m}">{MESI[int(m)-1][:3] if m else "?"}<small>{len(v)}</small></a>' for m,v in g.items())+'</nav>'
    body=''.join(f'<section class="ygroup" id="m{m}"><h2 class="yr">{MESI[int(m)-1].capitalize() if m else ""} {y} <small>{len(v)} testi</small></h2><ul class="entries">{"".join(entry(a,"../") for a in v)}</ul></section>' for m,v in g.items())
    i=ys.index(y) if y in ys else -1
    nav='<div class="ynav">'+(f'<a href="{ys[i-1]}.html">← {ys[i-1]}</a>' if i>0 else '<span></span>')+(f'<a href="{ys[i+1]}.html">{ys[i+1]} →</a>' if 0<=i<len(ys)-1 else '<span></span>')+'</div>'
    filt='<div class="filt"><input type="search" placeholder="Filtra per titolo o tema…" oninput="filtra(this.value)"><span id="fcount"></span></div>'
    content=f'<p class="crumb"><a href="../anni.html">Cronologia</a></p><header class="phead"><h1>{y}</h1><p class="meta">{len(l)} testi</p></header>{nav}{filt}{jump}{body}{nav}'
    open(os.path.join(OUT,'anni',f'{y}.html'),'w').write(page(str(y),content,'../','anni.html'))
# temi
_TWD=json.load(open(os.path.join(WORK,'temi_wikidata.json'))) if os.path.exists(os.path.join(WORK,'temi_wikidata.json')) else {}
_WDK={}
for _n,_e in _TWD.items():
    for _k in _risolvi(_lk(_n)): _WDK.setdefault(_k,_e)
def _wd(k): return _WDK.get(k) or _TWD.get(kwname(k)) or _TWD.get(k)
tlist=sorted([k for k in kwcount if kwcount[k]>=3],key=lambda k:norm(kwname(k)))
for k in tlist:
    l=sorted(inv[k],key=sortkey,reverse=True)
    co=collections.Counter(x for a in l for x in a['kws'] if x!=k)
    near=''.join(f'<a class="chip" href="{KWSLUG[x]}.html">{esc(kwname(x))} <small>{n}</small></a>' for x,n in co.most_common(16) if kwcount[x]>=3)
    _w=_wd(k); _wdl=(' · <a class="wd" href="https://www.wikidata.org/wiki/'+_w['id']+'" target="_blank" rel="noopener" title="'+esc(_w.get('desc',''))+'">scheda Wikidata '+_w['id']+' ↗</a>') if _w else ''
    _id=IDENT.get((_w or {}).get('id',''),{})
    _wdl+=(f' · <a class="wd" href="https://viaf.org/viaf/{_id["viaf"]}" target="_blank" rel="noopener">VIAF ↗</a>' if _id.get('viaf') else '')+(f' · <a class="wd" href="https://opac.sbn.it/nome/{_id["sbn"]}" target="_blank" rel="noopener">SBN ↗</a>' if _id.get('sbn') else '')+(f' · <a class="wd" href="https://www.geonames.org/{_id["geonames"]}" target="_blank" rel="noopener">GeoNames ↗</a>' if _id.get('geonames') else '')
    _tp,_st=TIPO.get(k,('non classificato',''))
    _fo=FORME.get(k,{})
    _fol='; '.join(f'«{esc(f)}» ({n})' for f,n in _fo.most_common()) if _fo else ''
    _amb=(f'<p class="note warn">Voce da verificare: {esc(AMBT[k])}. Se sai a chi o a che cosa si riferiscono i testi, <a href="mailto:lelomar@gmail.com?subject=correzione%20proposta%20progetto%20moscato">scrivilo</a> o <a href="https://github.com/lelomar/archivio-antonio-moscato/issues/new" target="_blank" rel="noopener">segnalalo su GitHub</a>.</p>' if k in AMBT else '')
    content=f'<p class="crumb"><a href="../temi.html">Temi</a> · <a href="../temi.html#tipo-{_tp.replace(" ","-")}">{esc(_VOC.ETI.get(_tp,_tp))}</a></p><header class="phead"><h1>{esc(kwname(k))}</h1><p class="meta">{len(l)} testi · <a href="../cerca.html#tema={urllib.parse.quote(k)}">apri nella ricerca avanzata</a>{_wdl}</p>'+(f'<p class="forme">Parole chiave originali: {_fol}</p>' if _fol else '')+f'{_amb}</header>'+(f'<div class="box near"><h4>Temi collegati</h4><div class="chips">{near}</div></div>' if near else '')+entries_by_year(l,'../',True)
    open(os.path.join(OUT,'temi',f'{KWSLUG[k]}.html'),'w').write(page(kwname(k),content,'../','temi.html'))
# rinvii per i temi unificati (vecchi indirizzi delle pagine dei temi)
_GEN={KWSLUG[k] for k in tlist}
for _ak,_av in ALIAS.items():
    _old=slugify(_ak)
    if isinstance(_av,list): continue
    _av=_risolvi(_av)[0]
    if _av in KWSLUG and kwcount.get(_av,0)>=3 and _old!=KWSLUG[_av] and _old not in _GEN:
        open(os.path.join(OUT,'temi',_old+'.html'),'w').write(f'<!doctype html><html lang="it"><head><meta charset="utf-8"><meta name="robots" content="noindex"><meta http-equiv="refresh" content="0; url={KWSLUG[_av]}.html"><link rel="canonical" href="{KWSLUG[_av]}.html"><title>Tema spostato</title></head><body><p>Questo tema è stato unificato: <a href="{KWSLUG[_av]}.html">{esc(kwname(_av))}</a>.</p></body></html>')
print('vocabolario',_VOC.run(OUT,WORK,kwcount,KWSLUG,kwname,ORIGKW,TIPO,AMBT,_wd,IDENT,{str(a['id']):a for a in arts}),flush=True)
json.dump({KWSLUG[k]:_wd(k)['id'] for k in kwcount if _wd(k)},open(os.path.join(WORK,'_temi_slug_wd.json'),'w'))
top=[k for k,_ in kwcount.most_common(70)]
mxk=kwcount[top[0]]
def cloud(pre,n=70):
    sel=top[:n]; ts=sorted(sel,key=lambda k:norm(kwname(k)))
    rank={k:i for i,k in enumerate(sel)}
    def lvl(k):
        i=rank[k]/len(sel)
        return 'c3' if i<.2 else 'c2' if i<.55 else 'c1'
    return '<div class="cloud">'+''.join(f'<a class="{lvl(k)}" href="{pre}temi/{KWSLUG[k]}.html" title="{kwcount[k]} testi">{esc(kwname(k))}<sup>{kwcount[k]}</sup></a>' for k in ts)+'</div>'
letters=collections.OrderedDict()
for k in tlist: letters.setdefault((norm(kwname(k))[:1] or '#').upper(),[]).append(k)
az='<nav class="jump">'+''.join(f'<a href="#l{L}">{L}</a>' for L in letters)+'</nav>'
groups=''.join(f'<section class="ygroup" id="l{L}"><h2 class="yr">{L}</h2><ul class="tlist">'+''.join(f'<li class="entry" data-t="{esc(norm(kwname(k)))}" data-tipo="{TIPO.get(k,("",""))[0].replace(" ","-")}"><a href="temi/{KWSLUG[k]}.html">{esc(kwname(k))}</a> <small>{kwcount[k]}</small></li>' for k in v)+'</ul></section>' for L,v in letters.items())
_tc=collections.Counter(TIPO.get(k,('non classificato',''))[0] for k in tlist)
tipobar='<div class="tipi" role="group" aria-label="Mostra per tipo"><button type="button" class="chip on" data-tipo="">Tutti <small>'+str(len(tlist))+'</small></button>'+''.join(f'<button type="button" class="chip" data-tipo="{t.replace(" ","-")}" id="tipo-{t.replace(" ","-")}">{_VOC.ETI[t]} <small>{_tc[t]}</small></button>' for t in _VOC.TIPI if _tc[t])+'</div>'
open(os.path.join(OUT,'temi.html'),'w').write(page('Temi',f'<header class="phead"><h1>Temi</h1><p class="lead">Persone, paesi, partiti e questioni attorno a cui ruotano i testi, ricavati dalle parole chiave che Moscato assegnava agli articoli. Qui {len(tlist)} temi con almeno tre testi.</p></header><h2 class="sec">I più ricorrenti</h2>{cloud("")}<h2 class="sec">Tutti i temi</h2><p class="hint">Ogni tema è ricondotto a un tipo: persona, organizzazione, luogo, evento storico, concetto o pubblicazione. Le parole chiave originali degli articoli restano come erano: ogni pagina di tema le riporta, e l’elenco completo è nei <a href="dati/parole-chiave-originali.csv">dati</a>. Come sono stati unificati e classificati i temi è spiegato nei <a href="criteri.html#temi">criteri di edizione</a>.</p>{tipobar}<div class="filt"><input type="search" placeholder="Cerca un tema, es. Trotskij" oninput="filtra(this.value)"><span id="fcount"></span></div><div class="tipi-f">{az}{groups}</div>','','temi.html'))
print('pages ok',len(tlist),flush=True)
docs_by_cat=collections.defaultdict(list)
for g,d in docs.items(): docs_by_cat[d.get('cat',0)].append((g,d))
def dmname(c): return DMCAT.get(c) or ('Altri documenti' if not c else 'Documenti')
parent={}
for p,ch in DMSUB.items():
    for c in ch:
        if p!=0 or c not in parent: parent[c]=p
def count(c,seen=()): return len(docs_by_cat.get(c,[]))+sum(count(x,seen+(c,)) for x in DMSUB.get(c,[]) if x not in seen and x!=c)
def fsize(n): return f'{n/1024:.0f} kB' if n<1048576 else f'{n/1048576:.1f} MB'

DOCJS=[]
def docitem(g,d,pre):
    t=esc(d.get('title') or d.get('filename') or f'Documento {g}')
    ds=clean(d['ldesc'],pre) if (d.get('ldesc') or '').strip() else ''
    if d.get('out'):
        ext=d['out'].rsplit('.',1)[-1].upper()
        main_href=pre+(d['page'] if d.get('page') else d['out'])
        extra=((f' <a class="badge" href="{pre}{d["out"]}" data-title="{t}">sfoglia il PDF</a>' if ext=='PDF' else f' <a class="badge" href="{pre}{d["out"]}" download>scarica {ext}</a>') if d.get('page') else '')+(' <span class="badge off" title="Il file è stato troncato a 1 MB al momento dell’archiviazione">incompleto</span>' if d.get('broken') else '')
        h=f'<a class="dl" href="{main_href}"><span class="ft ft-{ext.lower()}">{ext}</span><b>{t}</b></a><span class="bgs"><span class="badge">{fsize(d["size"])}{" · "+str(max(1,round(d["words"]/220)))+" min di lettura" if d.get("page") else ""}</span>{extra}</span>'
    else:
        h=f'<span class="dl off"><span class="ft">—</span><b>{t}</b></span><a class="badge ext" target="_blank" rel="noopener" href="{WB}http://antoniomoscato.altervista.org/index.php?option=com_docman&task=doc_download&gid={g}">non recuperato: prova online</a>'
    return f'<li class="doc entry" id="d{g}" data-t="{esc(norm((d.get("title") or "")+" "+BeautifulSoup(ds,"lxml").get_text(" ")))}">{h}<div class="desc">{ds}</div><span class="d">{esc((d.get("date") or "")[:10])}</span></li>'
def doclist(c,pre):
    it=sorted(docs_by_cat.get(c,[]),key=lambda x:(x[1].get('title') or '').lower())
    return '<ul class="docs">'+''.join(docitem(g,d,pre) for g,d in it)+'</ul>' if it else ''
for c in set(DMCAT)|set(docs_by_cat):
    subs=[x for x in DMSUB.get(c,[]) if x!=c and count(x)]
    chain=[]; p=parent.get(c)
    while p and p not in chain: chain.insert(0,p); p=parent.get(p)
    crumb='<a href="index.html">I grandi nodi del Novecento</a>'+''.join(f' › <a href="cat{p}.html">{esc(dmname(p))}</a>' for p in chain if p!=1)
    sub=''.join(f'<a class="card" href="cat{x}.html"><b>{esc(dmname(x))}</b><span>{count(x)} documenti</span></a>' for x in subs)
    content=f'<p class="crumb">{crumb}</p><header class="phead"><h1>{esc(dmname(c))}</h1><p class="meta">{count(c)} documenti</p></header>'+(f'<div class="cards">{sub}</div>' if sub else '')+doclist(c,'../')
    open(os.path.join(OUT,'documenti',f'cat{c}.html'),'w').write(page(dmname(c),content,'../','documenti/index.html'))
def dlink(gg,x):
    if x.get('page'): return f'{gg}.html'
    if x.get('out'): return '../../'+x['out']
    return f'../cat{x.get("cat",0)}.html#d{gg}'
for g,d in docs.items():
    if not d.get('page'): continue
    c=d.get('cat',0); chain=[]; p=c
    while p and p not in chain and p!=1: chain.insert(0,p); p=parent.get(p)
    crumb='<a href="../index.html">I grandi nodi del Novecento</a>'+''.join(f' › <a href="../cat{x}.html">{esc(dmname(x))}</a>' for x in chain)
    ext=d['out'].rsplit('.',1)[-1].upper(); t=d.get('title') or d.get('filename') or ''
    ds=clean(d['ldesc'],'../../') if (d.get('ldesc') or '').strip() else ''
    note='<p class="note">Testo estratto automaticamente dal PDF: impaginazione, note e tabelle possono risultare imprecise. Per la versione fedele apri il file originale.</p>' if ext=='PDF' else '<p class="note">Versione di lettura convertita dal file originale.</p>'
    if d.get('broken'): note+='<p class="note warn">Attenzione: il file originale è stato troncato a 1 MB al momento dell’archiviazione, quindi il testo è incompleto.</p>'
    content=f"""<div class="artgrid"><article class="art"><p class="crumb">{crumb}</p><h1>{esc(t)}</h1>
<p class="meta">{esc(dmname(c))}{' · pubblicato il '+hdate(d['iso']) if d.get('iso') else ''} · {rtime(d['words'])}</p>{f'<div class="lead">{ds}</div>' if ds else ''}
<p class="dlbar">{f'<a class="btn" href="../../{d["out"]}" data-title="{esc(t)}">Sfoglia il PDF originale</a><a class="btn alt" href="../../{d["out"]}" download>Scarica ({fsize(d["size"])})</a>' if ext=='PDF' else f'<a class="btn" href="../../{d["out"]}" download>Scarica il file originale ({ext}, {fsize(d["size"])})</a>'}</p>{note}
<div class="testo doctext" id="testo">{BeautifulSoup('<div>'+(d.get('_body') or '')+'</div>','lxml').div.decode_contents() if False else ''}</div></article>
<aside class="side"><div class="box"><h4>Questo documento</h4><p>{esc(dmname(c))}<br>{ext} · {fsize(d['size'])}<br>{rtime(d['words'])}</p><div class="tools"><button type="button" onclick="fs(-1)" aria-label="Riduci il testo">A−</button><button type="button" onclick="fs(1)" aria-label="Ingrandisci il testo">A+</button><button type="button" onclick="window.print()">Stampa</button></div></div>
<div class="box"><h4>Nella stessa sezione</h4><ul class="mini-list">{''.join(f'<li><a href="{dlink(gg,x)}">{esc(x.get("title") or "")}</a></li>' for gg,x in sorted(docs_by_cat.get(c,[]),key=lambda z:(z[1].get("title") or "").lower()) if gg!=g)}</ul></div></aside></div>"""
    open(os.path.join(OUT,'documenti','testo',f'{g}.html'),'w').write(page(t,content.replace('<div class="testo doctext" id="testo"></div>','<div class="testo doctext" id="testo">'+d['_body']+'</div>'),'../../','documenti/index.html','pg-art',d.get('lang','it')))
for g,d in docs.items():
    dtxt=BeautifulSoup(d.get('ldesc') or '','lxml').get_text(' ').strip()
    href=d.get('page') or d.get('out') or f'documenti/cat{d.get("cat",0)}.html#d{g}'
    exc=dtxt or (d.get('text','')[:240].rsplit(' ',1)[0]+'…' if d.get('text') else '')
    DOCJS.append(['d'+str(g),d.get('title') or d.get('filename') or '',d.get('iso',''),'doc',d.get('lang','it'),[],exc,d.get('words',0),href,dmname(d.get('cat',0)),(d.get('out') or '').rsplit('.',1)[-1].upper() if d.get('out') else '',1 if d.get('text') else 0])
topd=list(dict.fromkeys(DMSUB.get(1,[])+[x for x in DMSUB.get(0,[]) if x!=1 and parent.get(x,0)==0]))
topd=[x for x in topd if count(x)]
dcards=''.join(f'<a class="card" href="{{pre}}documenti/cat{x}.html"><b>{esc(dmname(x))}</b><span>{count(x)} documenti</span></a>' for x in topd)
nrec=sum(1 for d in docs.values() if d.get('out'))
# --- conteggi: unica fonte per tutti i numeri dichiarati (dati/conteggi.json) ---
_rpc=os.path.join(root,'recupero','rapporto.json'); _rpc=json.load(open(_rpc)) if os.path.exists(_rpc) else {}
_din=[d for d in docs.values() if d.get('out')]; _dout=[(g,d) for g,d in docs.items() if not d.get('out')]
CONTI={'articoli':len(arts),'articoli_joomla_estratti':len(D['arts']),'articoli_wordpress':len(D['wp']),'articoli_wordpress_unici':len(WP),
 'pagine_di_servizio_escluse':1+len(DROP_ART),'doppioni_uniti':len(DUP_ART),
 'documenti':len(docs),'documenti_in_archivio':nrec,'documenti_integri':sum(1 for d in _din if not d.get('broken')),'documenti_incompleti':sum(1 for d in _din if d.get('broken')),
 'documenti_assenti':len(_dout),'documenti_audio_video':sum(1 for g,d in _dout if dmname(d.get('cat',0))=='Audio e video'),
 'documenti_ritrovati_dopo':sum(1 for g,d in docs.items() if d.get('out') and (_rpc.get(str(g)) or {}).get('file')),
 'documenti_ritrovati_dopo_incompleti':sum(1 for g,d in docs.items() if d.get('out') and d.get('broken') and (_rpc.get(str(g)) or {}).get('file'))}
CONTI['documenti_mancanti']=CONTI['documenti_assenti']-CONTI['documenti_audio_video']
CONTI['temi_con_pagina']=len(tlist); CONTI['temi_nel_vocabolario']=len(kwcount)
for _t in ('persona','organizzazione','luogo','evento','concetto','pubblicazione','non classificato'): CONTI['temi_'+_t.replace(' ','_')]=sum(1 for k in kwcount if TIPO.get(k,('',''))[0]==_t)
CONTI['temi_da_verificare']=len(AMBT)
CONTI['temi_con_wikidata']=sum(1 for k in kwcount if _wd(k))
CONTI['articoli_prima_della_pulizia']=CONTI['articoli_joomla_estratti']-1+CONTI['articoli_wordpress_unici']
assert CONTI['documenti_integri']+CONTI['documenti_incompleti']+CONTI['documenti_mancanti']+CONTI['documenti_audio_video']==CONTI['documenti'],CONTI
assert CONTI['articoli_prima_della_pulizia']-CONTI['pagine_di_servizio_escluse']+1-CONTI['doppioni_uniti']==CONTI['articoli'],CONTI
def _n(v): return f'{v:,}'.replace(',','.')
os.makedirs(os.path.join(OUT,'dati'),exist_ok=True)
json.dump(CONTI,open(os.path.join(OUT,'dati','conteggi.json'),'w'),ensure_ascii=False,indent=1)
_ci,_cn,_ca,_cm,_cv=(CONTI[k] for k in ('documenti_integri','documenti_incompleti','documenti_assenti','documenti_mancanti','documenti_audio_video'))
open(os.path.join(OUT,'documenti','index.html'),'w').write(page('I grandi nodi del Novecento',f'<header class="phead"><h1>I grandi nodi del Novecento</h1><p class="lead">Saggi, capitoli di libri esauriti e materiali d’archivio che il sito offriva in download: {len(docs)} documenti censiti. {nrec} sono qui e si aprono da questa pagina: {_ci} integri e {_cn} incompleti, troncati al primo megabyte. Gli altri {_ca} mancano: {_cm} non sono mai stati salvati dall’Internet Archive, {_cv} erano video o audio esterni.</p></header><div class="filt"><input type="search" placeholder="Filtra i documenti di questa pagina…" oninput="filtra(this.value)"><span id="fcount"></span></div><div class="cards">{dcards.replace("{pre}","../")}</div>'+doclist(1,'../')+doclist(0,'../')+'<p class="hint">Per cercare dentro tutti i documenti usa la <a href="../cerca.html">ricerca</a>.</p>','../','documenti/index.html'))
# data for JS
CATS={str(c):catname(c) for c in bycat}; CATS['doc']='Documenti · I grandi nodi del Novecento'
meta=[[str(a['id']),a['title'],a['date'],a['catid'],a['lang'],a['kws'],a['exc'],a['words']] for a in arts]
_T={str(a['id']):a['plain'] for a in arts}
_T.update({'d'+str(g):d['text'] for g,d in docs.items() if d.get('text')})
_parts=[];_cur={};_sz=0
for k,v in _T.items():
    _cur[k]=v; _sz+=len(v.encode('utf-8'))
    if _sz>12_000_000: _parts.append(_cur); _cur={}; _sz=0
if _cur: _parts.append(_cur)
for i,pp in enumerate(_parts,1):
    with open(os.path.join(OUT,'assets',f'testi-{i}.js'),'w') as f:
        f.write('window.TESTI=Object.assign(window.TESTI||{},'+json.dumps(pp,ensure_ascii=False,separators=(',',':'))+');')
NTESTI=len(_parts)
_old=os.path.join(OUT,'assets','testi.js')
if os.path.exists(_old): os.remove(_old)
with open(os.path.join(OUT,'assets','meta.js'),'w') as f:
    f.write('window.META='+json.dumps({'arts':meta,'cats':CATS,'catorder':[c for c in cat_order if c in bycat]+['doc'],'kwn':{k:kwname(k) for k in kwcount},'kwslug':{k:KWSLUG[k] for k in kwcount if kwcount[k]>=3},'ntesti':NTESTI,'docs':DOCJS},ensure_ascii=False,separators=(',',':'))+';')
print('data ok',flush=True)
recent=sorted(arts,key=sortkey,reverse=True)
recent=[a for a in recent if 'ricostruzione' not in a['title'].lower()][:6]
lead=recent[0]
featured=''.join(entry(a,'') for a in recent[1:6])
nodes=''.join(f'<a class="card" href="documenti/cat{x}.html"><b>{esc(dmname(x))}</b><span>{count(x)} documenti</span></a>' for x in topd[:9])
chi='<a href="biografia.html">Chi era Antonio Moscato</a>' if 22 in A else ''
home=f'''<section class="hero"><div><p class="kick">Archivio 2009–2021 · {_n(len(arts))} articoli · {nrec} documenti su {len(docs)}</p><h1>Movimento operaio<span>Il sito di Antonio Moscato, ricostruito</span></h1>
<blockquote>Il sito «è nato dalla proposta di alcuni studenti di raccogliere e quindi non far disperdere una notevole quantità di saggi, articoli, libri ormai esauriti da tempo».<cite>Antonio Moscato, dalla pagina di benvenuto · {chi}</cite></blockquote></div>
<form class="bigsearch" onsubmit="return miniCerca(this)"><input name="q" type="search" placeholder="Cerca tra articoli e documenti: Togliatti, Grecia, Guevara…" aria-label="Cerca"><button>Cerca</button></form>
<p class="quick"><a href="progetto.html">Il progetto di recupero</a> · <a href="cerca.html">ricerca avanzata</a> · <a href="#" onclick="return aCaso()">un testo a caso</a></p></section>
<h2 class="sec">Le rubriche</h2><div class="rgrid">{"".join(rcard(c) for c in main_c[:6])}</div><p class="more-l"><a href="attualita.html">Tutte le rubriche →</a></p>
<div class="two"><section><h2 class="sec">Temi ricorrenti</h2>{cloud("",30)}<p class="more-l"><a href="temi.html">Indice completo dei temi →</a></p></section>
<section><h2 class="sec">Dodici anni di scritti</h2>{histo("")}<p class="hint">Testi pubblicati per anno: clicca una colonna per aprirlo.</p></section></div>
<section id="oggi" class="oggi"></section>
<h2 class="sec">I grandi nodi del Novecento</h2><p class="lead">I saggi e i libri esauriti, materia del lavoro di storico del movimento operaio.</p><div class="cards">{nodes}</div><p class="more-l"><a href="documenti/index.html">Tutti i documenti →</a></p>
<h2 class="sec">Gli ultimi testi</h2><article class="leadart"><div class="em"><time>{hdate(lead['date'])}</time> <a class="rb" href="categorie/c{lead['catid']}.html">{esc(catname(lead['catid']))}</a></div><h3><a href="articoli/{lead['id']}.html">{esc(lead['title'])}</a></h3><p class="exc">{esc(lead['exc'])}</p></article><ul class="entries">{featured}</ul>
<script src="assets/meta.js"></script><script src="assets/oggi.js"></script>'''
open(os.path.join(OUT,'index.html'),'w').write(page('Home',home,'','index.html','pg-home'))
search='''<header class="phead"><h1>Ricerca</h1><p class="lead">Cerca in tutto il testo dei 2.928 articoli e tra i documenti. Restringi con i filtri a sinistra; i risultati si aggiornano mentre scrivi.</p></header>
<form class="bigsearch" onsubmit="S.run();return false"><input id="q" type="search" placeholder="Parole o “frase esatta”…" autocomplete="off" aria-label="Testo da cercare"><button>Cerca</button></form>
<div class="sopts"><label><input type="radio" name="dove" value="all" checked> in tutto il testo</label><label><input type="radio" name="dove" value="tit"> solo nei titoli e temi</label>
<span class="sp"></span><label>Ordina per <select id="ord"><option value="rel">pertinenza</option><option value="new">più recenti</option><option value="old">meno recenti</option></select></label></div>
<p id="status" class="hint" role="status" aria-live="polite"></p>
<div class="sgrid"><aside class="facets" id="facets">
<div class="box"><h4>Periodo</h4><div class="yrange"><select id="y1"></select><span>–</span><select id="y2"></select></div><div id="fhist" class="histo small"></div></div>
<div class="box"><h4>Rubriche</h4><div id="fcat"></div></div>
<div class="box"><h4>Lingua</h4><div id="flang"></div></div>
<div class="box"><h4>Temi</h4><div id="ftema-sel" class="chips"></div><input id="tq" type="search" placeholder="aggiungi un tema…" list="tdl"><datalist id="tdl"></datalist><div id="ftema" class="chips"></div></div>
<button class="reset" onclick="S.reset()">Azzera filtri</button></aside>
<section class="results"><div id="active" class="chips"></div><div id="dres"></div><ol id="res" class="entries"></ol><nav id="pager" class="pager"></nav></section></div>
<script src="assets/meta.js"></script><script src="assets/cerca.js"></script>'''
open(os.path.join(OUT,'cerca.html'),'w').write(page('Ricerca',search,'','cerca.html','pg-search'))
for f in ['indice.js']:
    p=os.path.join(OUT,'assets',f)
    if os.path.exists(p): os.remove(p)


_og='<header class="phead"><p class="kick">Accadde oggi</p><h1 id="ot"></h1><p class="lead">Cosa pubblicava Antonio Moscato sul suo sito in questo giorno dell’anno, dal 2009 al 2021. Scegli una data o scorri i giorni.</p><p class="meta" id="on"></p></header><div class="ocontrols"><button type="button" id="oprev">← Giorno prima</button><select id="od" aria-label="Giorno"></select><select id="om" aria-label="Mese"></select><button type="button" id="onext">Giorno dopo →</button><button type="button" id="otoday">Oggi</button></div><div id="oggi-pagina"><ul class="entries" id="ol"></ul></div><p class="hint">Il pulsante «Copia per i social» prepara una riga pronta da incollare, con il link al testo.</p><script src="assets/meta.js"></script><script src="assets/oggi.js"></script>'
open(os.path.join(OUT,'accadde-oggi.html'),'w').write(page('Accadde oggi',_og,'','accadde-oggi.html'))
_pt=open(os.path.join(WORK,'progetto.html')).read()
for _k,_v in CONTI.items(): _pt=_pt.replace('{{'+_k+'}}',_n(_v))
_rpf=os.path.join(root,'recupero','rapporto.json'); _mif=os.path.join(root,'recupero','mancanti.json')
_rp=json.load(open(_rpf)) if os.path.exists(_rpf) else {}
_mi=json.load(open(_mif)) if os.path.exists(_mif) else [{'gid':g,'title':d.get('title',''),'filename':d.get('filename','')} for g,d in sorted(docs.items()) if not d.get('out')]
def _sec(c):
    ch=[];x=c
    while x and x not in (0,1) and x not in ch: ch.insert(0,x); x=parent.get(x)
    return ' › '.join(dmname(y) for y in ch if DMCAT.get(y)) or 'Senza sezione'
def _fn(f):
    f=urllib.parse.unquote((f or '').replace('Link to ','')).split('?')[0]
    return '—' if not f or f=='Unknown' else f
rows=[];inc=[]
for m in _mi:
    g=m['gid']
    if (_rp.get(str(g)) or {}).get('file'): continue
    d=docs.get(g,{}); s=_sec(d.get('cat',0))
    if s.startswith('Audio'): continue
    rows.append((s,m['title'].replace(' hot!',''),_fn(m['filename']),(d.get('date') or '')[:10],g))
for g,d in docs.items():
    if d.get('broken'): inc.append((_sec(d.get('cat',0)),(d.get('title') or '').replace(' hot!',''),_fn(d.get('filename')),(d.get('date') or '')[:10],g))
def _tab(rr):
    rr.sort(key=lambda r:(r[0],r[1].lower())); out=[]; cur=None
    for s,t,f,dt,g in rr:
        if s!=cur: out.append(f'<tr class="sez"><th colspan="3">{esc(s)}</th></tr>'); cur=s
        out.append(f'<tr><td><a href="documenti/cat{docs.get(g,{}).get("cat",0)}.html#d{g}">{esc(t)}</a></td><td class="fn">{esc(f)}</td><td class="dt">{esc(dt)}</td></tr>')
    return '<div class="tw"><table class="mancanti"><thead><tr><th>Titolo</th><th>Nome del file originale</th><th>Pubblicato</th></tr></thead><tbody>'+''.join(out)+'</tbody></table></div>'
_mhtml=f"""<h2 id="mancanti">L’elenco dei documenti da ritrovare</h2>
<p>Questi sono i {len(rows)} documenti mai salvati dall’Internet Archive, divisi per sezione. Il nome del file originale, quando è noto, è l’indizio più utile per cercarli su un vecchio computer o in una casella di posta. Va bene qualsiasi versione: il file, una bozza, una scansione del testo stampato.</p>
<details open><summary>{len(rows)} documenti mancanti</summary>{_tab(rows)}</details>
<p>E questi sono i {len(inc)} documenti recuperati solo a metà, troncati al primo megabyte: anche di questi servirebbe una copia integrale.</p>
<details><summary>{len(inc)} documenti incompleti</summary>{_tab(inc)}</details>
<p>Chi ne ha una copia può scrivermi a <a href="mailto:lelomar@gmail.com">lelomar@gmail.com</a> o attraverso <a href="https://lelomar.substack.com" target="_blank" rel="noopener">lelomar.substack.com</a>, indicando il titolo. Ogni documento ha anche una scheda pubblica sulla lavagna <a href="https://github.com/users/lelomar/projects/2" target="_blank" rel="noopener">Caccia ai documenti di Antonio Moscato</a>: lì si può commentare, segnalare di averlo o allegare direttamente il file, e seguire a che punto è la ricerca.</p>"""
_pt=_pt.replace('<!--MANCANTI-->',_mhtml)
def _md(md):
    """Converte il registro delle versioni (Markdown semplice) in HTML."""
    def inl(t):
        t=esc(t)
        t=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',lambda m:'<a href="'+(m.group(2) if m.group(2).startswith('http') else 'https://github.com/lelomar/archivio-antonio-moscato/blob/main/'+m.group(2))+'" target="_blank" rel="noopener">'+m.group(1)+'</a>',t)
        t=re.sub(r'\*\*([^*]+)\*\*',r'<b>\1</b>',t); t=re.sub(r'\*([^*]+)\*',r'<em>\1</em>',t); t=re.sub(r'`([^`]+)`',r'<code>\1</code>',t)
        return t
    out=[];inlist=False
    for ln in md.splitlines():
        if ln.startswith('# '): continue
        if ln.startswith('- '):
            if not inlist: out.append('<ul class="vers">'); inlist=True
            out.append('<li>'+inl(ln[2:])+'</li>'); continue
        if inlist: out.append('</ul>'); inlist=False
        if ln.startswith('## '): out.append('<h3 class="vh">'+inl(re.sub(r'^\[([^\]]+)\]',r'\1',ln[3:]))+'</h3>')
        elif ln.startswith('### '): out.append('<h4 class="vk">'+inl(ln[4:])+'</h4>')
        elif ln.strip(): out.append('<p>'+inl(ln)+'</p>')
    if inlist: out.append('</ul>')
    return '\n'.join(out)
_cl=os.path.join(OUT,'CHANGELOG.md')
if os.path.exists(_cl):
    _pt=_pt.replace('<!--VERSIONI-->','<h2>Le versioni</h2>\n<details class="versioni"><summary>Che cosa è cambiato da una versione all’altra</summary>'+_md(open(_cl,encoding='utf-8').read())+'</details>')
open(os.path.join(OUT,'progetto.html'),'w').write(page('Sono rimasto seduto. L’archivio ritrovato di Antonio Moscato',f'<div class="artgrid"><article class="art progetto"><p class="crumb">Il progetto</p><h1>Sono rimasto seduto</h1><p class="meta">Perché esiste questa copia del sito di Antonio Moscato, come è stata fatta, cosa manca</p><div class="testo" id="testo">{_pt}</div></article><aside class="side"><div class="box"><h4>In breve</h4><p>Antonio Moscato (Roma 1938 – 2026)<br>Sito originale: 2009–2021<br>{len(arts)} articoli · {nrec} documenti su {len(docs)}<br>Ricostruito nell’ottobre 2026</p></div><div class="box"><h4>Per cominciare</h4><ul class="mini-list"><li><a href="biografia.html">Chi era Antonio Moscato</a></li><li><a href="documenti/index.html">I grandi nodi del Novecento</a></li><li><a href="attualita.html">Le rubriche</a></li><li><a href="cerca.html">La ricerca</a></li><li><a href="#mancanti">I documenti da ritrovare</a></li><li><a href="#tecnica">Codice e licenze</a></li></ul></div><div class="box"><h4>Codice aperto</h4><p><a href="https://github.com/lelomar/archivio-antonio-moscato" target="_blank" rel="noopener">github.com/lelomar/archivio-antonio-moscato</a><br>Codice GPL-3.0 · cura CC BY-NC-SA 4.0</p></div><div class="box"><h4>Copia di sicurezza</h4><p><a href="https://archive.org/details/archivio-antonio-moscato" target="_blank" rel="noopener">Internet Archive</a><br>archivio completo in ZIP, da scaricare e conservare<br><a href="https://doi.org/10.5281/zenodo.23670900" target="_blank" rel="noopener">DOI 10.5281/zenodo.23670900</a> · Zenodo</p></div></aside></div>','','','pg-art'))
_cf=os.path.join(WORK,'criteri.html')
if os.path.exists(_cf):
    open(os.path.join(OUT,'criteri.html'),'w').write(page('Criteri di edizione','<div class="artgrid"><article class="art progetto">'+open(_cf).read()+'</article></div>','','progetto.html'))
_bf=os.path.join(WORK,'biografia.html')
if os.path.exists(_bf):
    open(os.path.join(OUT,'biografia.html'),'w').write(page('Antonio Moscato (1938–2026)','<div class="artgrid"><article class="art progetto bio">'+open(_bf).read()+'</article></div>','','biografia.html'))
_byA=collections.defaultdict(list)
for a in arts: _byA[a['autore'] or 'Autore da identificare'].append(a)
def _li(a): return f'<li><a href="articoli/{a["id"]}.html">{esc(a["title"])}</a> <span class="d">{hdate(a["date"])}</span></li>'
_others=sorted([k for k in _byA if k not in ('Antonio Moscato','Autore da identificare')],key=lambda k:(-len(_byA[k]),k))
_idx=''.join(f'<details class="aut"><summary><b>{esc(k)}</b> <span class="d">{len(_byA[k])} test{"o" if len(_byA[k])==1 else "i"}</span></summary><ul class="plain">{"".join(_li(a) for a in sorted(_byA[k],key=sortkey))}</ul></details>' for k in _others)
_nm=len(_byA.get('Antonio Moscato',[])); _ni=sum(1 for a in arts if a['mosc'].startswith('introduzione')); _np=sum(1 for a in arts if a['mosc'].startswith('postilla'))
open(os.path.join(OUT,'autori.html'),'w').write(page('Gli autori',f'''<header class="rhead"><h1>Gli autori</h1><p class="lead">Il sito di Moscato era anche una piccola rivista: accanto ai suoi scritti ospitava articoli, interventi e traduzioni di {len(_others)} autori diversi, spesso presentati da una sua nota.</p><div class="rh-row"><p class="rh-n"><b>{_nm}</b> testi di Antonio Moscato</p><p class="rh-n"><b>{sum(len(_byA[k]) for k in _others)}</b> di altri autori</p><p class="rh-n"><b>{_ni+_np}</b> con una sua nota o postilla</p></div></header>
<p>Le attribuzioni sono state ricavate dalle firme presenti nei testi: la sigla «a.m.» o il nome di Moscato, le righe «di…», i nomi che aprono o chiudono l’articolo. Quelle incerte sono segnate come <em>da verificare</em> e raccolte nella pagina <a href="autori-da-verificare.html">Autori da verificare</a>, dove chiunque può aiutare a correggerle.</p>
<h2 class="sec">Gli altri autori</h2>{_idx}''','','autori.html'))
_ver=[a for a in arts if a['cert'] in ('media','bassa') or not a['autore']]
_byV=collections.defaultdict(list)
for a in _ver: _byV[a['autore'] or 'Autore da identificare'].append(a)
_vk=sorted(_byV,key=lambda k:(k=='Autore da identificare',k))
_vhtml=''.join(f'<h3 class="vh">{esc(k)} <span class="d">proposto per {len(_byV[k])} test{"o" if len(_byV[k])==1 else "i"}</span></h3><ul class="plain">{"".join(_li(a) for a in sorted(_byV[k],key=sortkey))}</ul>' for k in _vk)
_mt='mailto:'+MAILTO+'?subject='+_up.quote('correzione proposta progetto moscato')
open(os.path.join(OUT,'autori-da-verificare.html'),'w').write(page('Autori da verificare',f'''<header class="rhead"><h1>Autori da verificare</h1><p class="lead">Per {len(_ver)} testi non siamo sicuri di chi li abbia scritti. Il programma che ha letto l’archivio ha trovato un nome, ma potrebbe essere la persona di cui si parla e non l’autore; per alcuni testi non ha trovato nulla. Se li riconosci, aiutaci.</p></header>
<div class="segnala"><p><b>Come aiutare.</b> Apri il testo, e in fondo trovi «Segnala su GitHub» e «Scrivi una email»: il modulo e l’email arrivano già con l’indirizzo dell’articolo, a te basta scrivere il nome giusto e, se puoi, da dove lo sai. Chi non usa GitHub può scrivere direttamente a <a href="{_mt}">{MAILTO}</a>, con oggetto «correzione proposta progetto moscato».</p></div>
<p class="hint">Sono raggruppati per autore proposto: chi conosce bene un autore riconosce in un colpo d’occhio i testi che sono davvero suoi.</p>{_vhtml}''','','autori.html'))
for _i,_t in list(DROP_ART.items())+[(k,f'articoli/{v}.html') for k,v in DUP_ART.items()]:
    open(os.path.join(OUT,'articoli',f'{_i}.html'),'w').write(f'<!doctype html><html lang="it"><head><meta charset="utf-8"><meta name="robots" content="noindex"><meta http-equiv="refresh" content="0; url=../{_t}"><link rel="canonical" href="../{_t}"><title>Pagina spostata</title></head><body><p>Questa pagina è stata spostata: <a href="../{_t}">vai alla pagina</a>.</p></body></html>')
import subprocess as _sp, importlib.util as _iu
_spec=_iu.spec_from_file_location('link_archivio',os.path.join(WORK,'link_archivio.py')); _la=_iu.module_from_spec(_spec); _spec.loader.exec_module(_la)
print('link esterni',_la.run(OUT,WORK),flush=True)
_sp.run([sys.executable,os.path.join(WORK,'og.py'),OUT],check=False)
_spec=_iu.spec_from_file_location('seo',os.path.join(WORK,'seo.py')); _seo=_iu.module_from_spec(_spec); _spec.loader.exec_module(_seo)
_ai={str(a['id']):{'date':a['date'],'lang':a['lang'],'kws':[kwname(k) for k in a['kws']],'cat':catname(a['catid']),'autore':a['autore'],'cert':a['cert'],'mosc':a['mosc'],'scritto':a['scritto']} for a in arts}
print('seo pagine',_seo.run(OUT,_ai),flush=True)
_spec=_iu.spec_from_file_location('catalogo',os.path.join(WORK,'catalogo.py')); _cat=_iu.module_from_spec(_spec); _spec.loader.exec_module(_cat)
print('catalogo',_cat.run(OUT,root,WORK,arts,docs,catname,dmname,kwname),flush=True)
_spec=_iu.spec_from_file_location('provenienza',os.path.join(WORK,'provenienza.py')); _pv=_iu.module_from_spec(_spec); _spec.loader.exec_module(_pv)
print('provenienza',_pv.run(OUT,root,WORK,arts,docs,dmname,DUP_ART),flush=True)
_sp.run([sys.executable,os.path.join(WORK,'confronto.py'),root,OUT,'200'],check=False,stdout=_sp.DEVNULL)
_sp.run([sys.executable,os.path.join(WORK,'integrita.py'),OUT],check=False)
_sp.run([sys.executable,os.path.join(WORK,'verifica_conteggi.py'),OUT,root],check=False)
print('DONE',flush=True)
