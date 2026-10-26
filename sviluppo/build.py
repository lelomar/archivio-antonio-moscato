# Archivio Antonio Moscato – prima versione di Leonardo Lomartire (2026) – GPL-3.0 con attribuzione, vedi LICENZA.md
import os,re,json,sys,urllib.parse,html,unicodedata,shutil,collections,hashlib
from bs4 import BeautifulSoup, Comment
WORK=os.environ.get('MOSCATO_WORK',os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else '.')
import warnings; warnings.filterwarnings('ignore')
root=sys.argv[1]; OUT=sys.argv[2]
D=json.load(open(os.path.join(WORK,'data.json'))); D2=json.load(open(os.path.join(WORK,'data2.json')))
WB='https://web.archive.org/web/2016/'
def num(x):
    m=re.match(r'\s*(\d+)',x or ''); return int(m.group(1)) if m else None
def norm(t):
    t=unicodedata.normalize('NFKD',(t or '').lower()); t=''.join(c for c in t if not unicodedata.combining(c))
    return re.sub(r'\s+',' ',re.sub(r'[^a-z0-9ñ]+',' ',t)).strip()
def esc(t): return html.escape(t or '',quote=True)
MESI=['gennaio','febbraio','marzo','aprile','maggio','giugno','luglio','agosto','settembre','ottobre','novembre','dicembre']
def hdate(d):
    if not d or len(d)<10: return ''
    y,m,g=d[:10].split('-'); return f"{int(g)} {MESI[int(m)-1]} {y}"
for sub in ['articoli','categorie','documenti','documenti/file','anni','assets','assets/img']:
    os.makedirs(os.path.join(OUT,sub),exist_ok=True)
CATN={int(k):v for k,v in D2['catnames'].items()}
SEC_CATS=[28,20,57,6,7,8,32,52,9,19,31]
arts=[a for a in D['arts'] if a['id']!=2]
A={a['id']:a for a in arts}
def catname(c):
    if c in CATN: return CATN[c]
    return {2:'Pagine del sito',46:'Link proposti',58:'Varie'}.get(c,'Altri testi')
for a in arts:
    if a['catid'] not in CATN and a['catid'] not in (2,46,58): a['catid']=0
existing={norm(a['title']) for a in arts}
WP={}
for w in D['wp']:
    if norm(w['title']) in existing: continue
    wid='wp-'+re.sub(r'[^a-z0-9-]','',w['slug'].lower())[:60]
    WP[w['slug']]=wid
    arts.append({'id':wid,'title':w['title'],'date':w['date'],'catid':-1,'html':w['html'],'kw':'','src':w['src'],'slug':w['slug']})
CATN[-1]='Gli ultimi scritti (blog 2018-2021)'
tid={norm(a['title']):a['id'] for a in arts}
WPslug_all={w['slug']:tid.get(norm(w['title'])) for w in D['wp']}
A={a['id']:a for a in arts}
dmdocs={int(k):v for k,v in D2['dmdocs'].items()}
docs={}
for k,v in D['docs'].items():
    if not k.startswith('f:'): docs[int(k)]=dict(v)
for g,v in dmdocs.items():
    d=docs.setdefault(g,{})
    if not d.get('title'): d['title']=v['title']
    d['cat']=v['cat']; d['ldesc']=v.get('desc',''); d['date']=d.get('date') or v.get('date','')
_rp=os.path.join(root,'recupero','rapporto.json')
if os.path.exists(_rp):
    for _k,_v in json.load(open(_rp)).items():
        if _v and _v.get('file') and int(_k) in docs: docs[int(_k)]['file']=_v['file']; docs[int(_k)]['ext']=_v['ext']
def safe(t):
    t=unicodedata.normalize('NFKD',t); t=''.join(c for c in t if not unicodedata.combining(c))
    return re.sub(r'[^A-Za-z0-9._-]+','_',t).strip('_')[:80] or 'documento'
for g,d in docs.items():
    if d.get('file'):
        fn=d.get('filename') or (d.get('title') or 'doc')
        base,ext=os.path.splitext(fn)
        if d.get('ext')=='pdf' or not ext or len(ext)>5: ext='.'+d.get('ext','pdf')
        name=f"{g}-{safe(base)}{ext.lower()}"
        dst=os.path.join(OUT,'documenti','file',name)
        if not os.path.exists(dst): shutil.copyfile(os.path.join(root,d['file']),dst)
        d['out']='documenti/file/'+name; d['size']=os.path.getsize(dst)
DMCAT={int(k):v for k,v in D2['dmcat'].items()}; DMSUB={int(k):v for k,v in D2['dmsub'].items()}
def local_asset(path):
    p=urllib.parse.unquote(path).lstrip('/')
    p=re.sub(r'^(index\.php/)+','',p)
    if not p or p.endswith('.php'): return None
    full=os.path.join(root,p)
    if os.path.isfile(full):
        ext=os.path.splitext(p)[1].lower()
        name=hashlib.md5(p.encode()).hexdigest()[:10]+ext
        dst=os.path.join(OUT,'assets','img',name)
        if not os.path.exists(dst): shutil.copyfile(full,dst)
        return 'assets/img/'+name
    return None
SITE=re.compile(r'^(https?:)?//(www\.)?antoniomoscato\.altervista\.org(:80)?',re.I)
def rewrite(href,pre):
    if not href: return href,False
    h=html.unescape(href.strip())
    if h.startswith('javascript:'): return None,False
    if h.lower().startswith('file:'):
        fr=h.split('#',1)[1] if '#' in h else ''
        return ('#'+fr if fr else None),True
    if h.startswith(('mailto:','#')): return href,True
    internal = bool(SITE.match(h)) or not re.match(r'^[a-z]+:',h,re.I)
    if not internal: return href,False
    path=SITE.sub('',h); u=urllib.parse.urlparse(path); q=urllib.parse.parse_qs(u.query)
    opt=q.get('option',[''])[0]; view=q.get('view',[''])[0]; task=q.get('task',[''])[0]
    absu='http://antoniomoscato.altervista.org'+(path if path.startswith('/') else '/'+path)
    if opt=='com_content' and view=='article':
        i=num(q.get('id',[''])[0])
        if i in A: return pre+f'articoli/{i}.html',True
        return WB+absu,False
    if opt=='com_content' and view=='category':
        c=num(q.get('id',[''])[0])
        if c in CATN: return pre+f'categorie/c{c}.html',True
    if opt=='com_content' and view=='section': return pre+'attualita.html',True
    if opt=='com_search':
        w=q.get('searchword',[''])[0]
        return pre+'cerca.html'+('#q='+urllib.parse.quote(w) if w else ''),True
    if opt=='com_docman':
        g=num(q.get('gid',[''])[0])
        if task in ('doc_download','doc_view','doc_details') and g in docs:
            if docs[g].get('page'): return pre+docs[g]['page'],True
            if docs[g].get('out'): return pre+docs[g]['out'],True
            return pre+f'documenti/cat{docs[g].get("cat",0)}.html#d{g}',True
        if task=='cat_view' and g in DMCAT: return pre+f'documenti/cat{g}.html',True
        return pre+'documenti/index.html',True
    if opt=='' and u.path in ('','/','/index.php') and not u.query: return pre+'index.html',True
    slug=u.path.strip('/')
    if slug in WPslug_all:
        t=WPslug_all[slug]
        if t is not None: return pre+f'articoli/{t}.html',True
    la=local_asset(u.path)
    if la: return pre+la,True
    return WB+absu,False
KEEPSTY=re.compile(r'(text-align\s*:\s*[a-z]+|margin-left\s*:\s*[0-9.]+(cm|px|em|pt))',re.I)
def clean(html_s,pre):
    s=BeautifulSoup(html_s,'lxml'); body=s.body or s
    for t in body.find_all(['script','style','noscript','form','input','button','link','meta','select','textarea']): t.decompose()
    for c in body.find_all(string=lambda x:isinstance(x,Comment)): c.extract()
    for t in body.select('.addthis_toolbox, .addthis_button, .sharedaddy, .jp-relatedposts, .pagenav, .wp-block-buttons'): t.decompose()
    for t in body.find_all('a'):
        hh=t.get('href') or ''
        if t.get_text(strip=True) in ('Tweet','Condividi') or 'twitter.com/share' in hh or 'facebook.com/sharer' in hh or 'addthis.com' in hh: t.decompose()
    for t in body.find_all(['iframe','embed','object']):
        src=t.get('src') or t.get('data') or ''
        if re.search(r'facebook\.com/plugins|platform\.twitter|addthis|plusone|altervista',src): t.decompose(); continue
        if src:
            if src.startswith('//'): src='https:'+src
            n=s.new_tag('p'); n['class']='embed'; a=s.new_tag('a',href=src); a.string='▶ Contenuto multimediale incorporato (richiede internet)'; n.append(a); t.replace_with(n)
        else: t.decompose()
    for t in body.find_all(['font','span']): t.unwrap()
    for t in body.find_all(re.compile(r'^o:')): t.unwrap()
    for t in list(body.find_all(True)):
        if t.parent is None and t is not body: continue
        st=t.get('style','') or ''
        keep='; '.join(m.group(1) for m in KEEPSTY.finditer(st))
        al=t.get('align'); cls=t.get('class')
        t.attrs={k:v for k,v in t.attrs.items() if k in ('href','src','alt','title','colspan','rowspan','id')}
        if cls and 'embed' in cls: t['class']='embed'
        if keep: t['style']=keep
        elif al in ('center','right','justify') and t.name in ('p','h1','h2','h3','h4','div','td'): t['style']='text-align:'+al
        if t.name=='a':
            h,ok=rewrite(t.get('href'),pre)
            if h is None: t.unwrap(); continue
            if h: t['href']=h
            if h and not ok and h.startswith('http'): t['target']='_blank'; t['rel']='noopener'; t['class']='ext'
        elif t.name=='img':
            src=t.get('src','')
            h,ok=rewrite(src,pre)
            if ok and h and 'assets/img/' in h: t['src']=h; t['loading']='lazy'
            elif src.startswith(('http','//')) and not SITE.match(src): t['loading']='lazy'
            else: t.decompose()
    out=body.decode_contents() if body.name in ('body','html','[document]') else str(body)
    out=re.sub(r'(?:<p>\s*(?:(?:&nbsp;|<br/?>)\s*)*</p>\s*){2,}','<p></p>',out)
    return out
NAV=[('index.html','Home'),('attualita.html','Attualità e polemiche'),('documenti/index.html','I grandi nodi del Novecento'),('anni.html','Per anno'),('cerca.html','Cerca')]
def page(title,content,pre,active=''):
    nav=''.join(f'<a href="{pre}{h}"{" class=on" if h==active else ""}>{esc(t)}</a>' for h,t in NAV)
    return f'''<!doctype html><html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} · Movimento operaio – La pagina di Antonio Moscato</title><link rel="stylesheet" href="{pre}assets/stile.css"></head>
<body><header class="top"><div class="wrap"><a class="brand" href="{pre}index.html"><span class="k">Movimento operaio</span><span class="s">La pagina di Antonio Moscato</span></a>
<nav>{nav}</nav></div></header><main class="wrap">{content}</main>
<footer class="wrap foot"><p>Ricostruzione statica, consultabile offline, del sito <em>antoniomoscato.altervista.org</em> (2009–2021), ricavata dalle copie conservate dall’Internet Archive. I link segnati con ↗ portano a pagine esterne o non recuperate e richiedono una connessione.</p></footer></body></html>'''
def sortkey(a): return (a['date'] or '0000', str(a['id']))
def li(a,pre,cat=False):
    c=f'<span class="cat">{esc(catname(a["catid"]))}</span>' if cat else ''
    return f'<li><a href="{pre}articoli/{a["id"]}.html">{esc(a["title"])}</a><span class="d">{hdate(a["date"])}</span>{c}</li>'
def bylist(items,pre):
    out=[]; cur=None
    for a in items:
        y=a['date'][:4] or 's.d.'
        if y!=cur:
            if cur is not None: out.append('</ul>')
            out.append(f'<h3 class="yr">{y}</h3><ul class="list">'); cur=y
        out.append(li(a,pre))
    if cur is not None: out.append('</ul>')
    return ''.join(out)
bycat=collections.defaultdict(list)
for a in arts: bycat[a['catid']].append(a)
for c in bycat: bycat[c].sort(key=sortkey,reverse=True)
BASEKW='movimento operaio, anticapitalismo, antistalinismo, democrazia operaia, internazionalismo, rivoluzione'
idx=[]; total=0
for a in arts:
    pre='../'; body=clean(a['html'],pre)
    lst=bycat[a['catid']]; i=lst.index(a)
    prev=lst[i+1] if i+1<len(lst) else None; nxt=lst[i-1] if i>0 else None
    pn=(f'<a class="pn" href="{nxt["id"]}.html"><small>← più recente</small>{esc(nxt["title"])}</a>' if nxt else '<span></span>')
    pn+=(f'<a class="pn r" href="{prev["id"]}.html"><small>precedente →</small>{esc(prev["title"])}</a>' if prev else '<span></span>')
    crumb=('<a href="../attualita.html">Attualità e polemiche</a> › ' if a['catid'] in SEC_CATS else '')+f'<a href="../categorie/c{a["catid"]}.html">{esc(catname(a["catid"]))}</a>'
    orig=WB+('http://antoniomoscato.altervista.org/index.php?option=com_content&view=article&id=%s'%a['id'] if isinstance(a['id'],int) else 'https://antoniomoscato.altervista.org/'+a.get('slug','')+'/')
    kw=''
    k=[x.strip() for x in (a.get('kw') or '').split(',') if x.strip() and x.strip().lower() not in BASEKW]
    if k: kw='<p class="kw">'+' · '.join(esc(x) for x in k[:12])+'</p>'
    content=f'<article class="art"><p class="crumb">{crumb}</p><h1>{esc(a["title"])}</h1><p class="meta">{hdate(a["date"])}</p>{kw}<div class="testo">{body}</div><p class="orig"><a href="{orig}" target="_blank" rel="noopener">Pagina originale sulla Wayback Machine ↗</a></p></article><nav class="pnav">{pn}</nav>'
    open(os.path.join(OUT,'articoli',f'{a["id"]}.html'),'w').write(page(a['title'],content,pre))
    txt=norm(BeautifulSoup(body,'lxml').get_text(' ')); total+=len(txt)
    idx.append([str(a['id']),a['title'],a['date'],catname(a['catid']),txt])
    if len(idx)%200==0: print("art",len(idx),flush=True)
cat_order=[c for c in SEC_CATS if c in bycat]+[-1]+[c for c in bycat if c not in SEC_CATS and c!=-1]
for c in cat_order:
    if c not in bycat: continue
    cr='<a href="../attualita.html">Attualità e polemiche</a>' if c in SEC_CATS else ''
    content=f'<p class="crumb">{cr}</p><h1>{esc(catname(c))}</h1><p class="meta">{len(bycat[c])} testi</p>'+bylist(bycat[c],'../')
    open(os.path.join(OUT,'categorie',f'c{c}.html'),'w').write(page(catname(c),content,'../'))
def span(c):
    ys=[a['date'][:4] for a in bycat[c] if a['date']]; return f'{min(ys)}–{max(ys)}' if ys else ''
cards=''.join(f'<a class="card" href="categorie/c{c}.html"><b>{esc(catname(c))}</b><span>{len(bycat[c])} testi · {span(c)}</span></a>' for c in cat_order if c in bycat and (c in SEC_CATS or c==-1))
others=''.join(f'<li><a href="categorie/c{c}.html">{esc(catname(c))}</a><span class="d">{len(bycat[c])} testi</span></li>' for c in cat_order if c in bycat and c not in SEC_CATS and c!=-1)
open(os.path.join(OUT,'attualita.html'),'w').write(page('Attualità e polemiche',f'<h1>Attualità e polemiche</h1><p class="lead">Articoli, commenti a caldo e polemiche pubblicati sul sito, nelle rubriche originali.</p><div class="cards">{cards}</div><h3 class="yr">Altre pagine</h3><ul class="list">{others}</ul>','','attualita.html'))
years=collections.defaultdict(list)
for a in arts: years[a['date'][:4] or 's.d.'].append(a)
ylinks=''.join(f'<a class="card y" href="anni/{y}.html"><b>{y}</b><span>{len(years[y])} testi</span></a>' for y in sorted(years,reverse=True))
open(os.path.join(OUT,'anni.html'),'w').write(page('Per anno',f'<h1>Archivio per anno</h1><div class="cards">{ylinks}</div>','','anni.html'))
for y,l in years.items():
    l.sort(key=sortkey,reverse=True); out=[]; cm=None
    for a in l:
        m=a['date'][5:7]
        if m!=cm:
            if cm is not None: out.append('</ul>')
            out.append(f'<h3 class="yr">{MESI[int(m)-1].capitalize() if m else ""} {y}</h3><ul class="list">'); cm=m
        out.append(li(a,'../',True))
    out.append('</ul>')
    open(os.path.join(OUT,'anni',f'{y}.html'),'w').write(page(str(y),f'<p class="crumb"><a href="../anni.html">Per anno</a></p><h1>{y}</h1><p class="meta">{len(l)} testi</p>'+''.join(out),'../'))
docs_by_cat=collections.defaultdict(list)
for g,d in docs.items(): docs_by_cat[d.get('cat',0)].append((g,d))
def dmname(c): return DMCAT.get(c) or ('Altri documenti' if not c else 'Documenti')
parent={}
for p,ch in DMSUB.items():
    for c in ch:
        if p!=0 or c not in parent: parent[c]=p
def count(c,seen=()):
    return len(docs_by_cat.get(c,[]))+sum(count(x,seen+(c,)) for x in DMSUB.get(c,[]) if x not in seen and x!=c)
def fsize(n): return f'{n/1024:.0f} kB' if n<1048576 else f'{n/1048576:.1f} MB'
def doclist(c,pre):
    out=[]
    for g,d in sorted(docs_by_cat.get(c,[]),key=lambda x:(x[1].get('title') or '').lower()):
        t=esc(d.get('title') or d.get('filename') or f'Documento {g}')
        ds=clean(d['ldesc'],pre) if (d.get('ldesc') or '').strip() else ''
        if d.get('out'):
            link=f'<a class="dl" href="{pre}{d["out"]}">{t}</a><span class="badge">{d["out"].rsplit(".",1)[-1].upper()} · {fsize(d["size"])}</span>'
        else:
            link=f'<span class="miss">{t}</span><span class="badge off">non recuperato</span> <a class="ext" target="_blank" rel="noopener" href="{WB}http://antoniomoscato.altervista.org/index.php?option=com_docman&task=doc_download&gid={g}">prova sulla Wayback ↗</a>'
        out.append(f'<li id="d{g}">{link}<span class="d">{esc(d.get("date",""))}</span><div class="desc">{ds}</div></li>')
    return '<ul class="docs">'+''.join(out)+'</ul>' if out else ''
for c in set(DMCAT)|set(docs_by_cat):
    subs=[x for x in DMSUB.get(c,[]) if x!=c and count(x)]
    chain=[]; p=parent.get(c)
    while p and p not in chain: chain.insert(0,p); p=parent.get(p)
    crumb='<a href="index.html">I grandi nodi del Novecento</a>'+''.join(f' › <a href="cat{p}.html">{esc(dmname(p))}</a>' for p in chain if p!=1)
    sub=''.join(f'<a class="card" href="cat{x}.html"><b>{esc(dmname(x))}</b><span>{count(x)} documenti</span></a>' for x in subs)
    content=f'<p class="crumb">{crumb}</p><h1>{esc(dmname(c))}</h1>'+(f'<div class="cards">{sub}</div>' if sub else '')+doclist(c,'../')
    open(os.path.join(OUT,'documenti',f'cat{c}.html'),'w').write(page(dmname(c),content,'../'))
top=list(dict.fromkeys(DMSUB.get(1,[])+[x for x in DMSUB.get(0,[]) if x!=1 and parent.get(x,0)==0]))
top=[x for x in top if count(x)]
cards=''.join(f'<a class="card" href="cat{x}.html"><b>{esc(dmname(x))}</b><span>{count(x)} documenti</span></a>' for x in top)
nrec=sum(1 for d in docs.values() if d.get('out'))
open(os.path.join(OUT,'documenti','index.html'),'w').write(page('I grandi nodi del Novecento',f'<h1>I grandi nodi del Novecento</h1><p class="lead">Saggi, libri esauriti e materiali d’archivio che il sito metteva a disposizione: {len(docs)} documenti, {nrec} dei quali recuperati e scaricabili da qui.</p><div class="cards">{cards}</div>'+doclist(1,'../')+doclist(0,'../'),'../','documenti/index.html'))
LIM=8000 if total>45_000_000 else 10**9
with open(os.path.join(OUT,'assets','indice.js'),'w') as f:
    f.write('window.INDICE='+json.dumps([[i,t,d,c,x[:LIM]] for i,t,d,c,x in idx],ensure_ascii=False,separators=(',',':'))+';')
open(os.path.join(OUT,'cerca.html'),'w').write(page('Cerca','''<h1>Cerca nel sito</h1><form class="search" onsubmit="go();return false"><input id="q" type="search" placeholder="Per esempio: Togliatti Spagna" autofocus><button>Cerca</button></form>
<p class="hint">Trova i testi che contengono tutte le parole indicate; maiuscole e accenti non contano. Una frase tra virgolette viene cercata esatta. La prima ricerca può impiegare qualche secondo.</p><div id="res"></div>
<script src="assets/indice.js"></script><script src="assets/cerca.js"></script>''','','cerca.html'))
recent=sorted(arts,key=sortkey,reverse=True)[:15]
rl=''.join(li(a,'') for a in recent)
chi='<a href="articoli/22.html">Chi è Antonio Moscato</a>' if 22 in A else ''
arc='<a href="articoli/74.html">Indice dell’Archivio</a>' if 74 in A else ''
links=' · '.join(x for x in [chi,arc,'<a href="cerca.html">Cerca nel sito</a>'] if x)
home=f'''<section class="hero"><h1>Movimento operaio<span>La pagina di Antonio Moscato</span></h1>
<blockquote>Il sito «è nato dalla proposta di alcuni studenti di raccogliere e quindi non far disperdere una notevole quantità di saggi, articoli, libri ormai esauriti da tempo».<cite>Antonio Moscato, dalla pagina di benvenuto</cite></blockquote>
<p class="links">{links}</p></section>
<div class="cards big"><a class="card" href="attualita.html"><b>Attualità e polemiche</b><span>{len(arts)} articoli, 2009–2021</span></a>
<a class="card" href="documenti/index.html"><b>I grandi nodi del Novecento</b><span>{len(docs)} saggi e documenti</span></a>
<a class="card" href="anni.html"><b>Per anno</b><span>la cronologia completa</span></a></div>
<h2 class="sec">Gli ultimi testi pubblicati</h2><ul class="list">{rl}</ul>'''
open(os.path.join(OUT,'index.html'),'w').write(page('Home',home,'','index.html'))
print('articles',len(arts),'wp-unique',len(WP),'docs',len(docs),'recovered',nrec,'index chars',total)
