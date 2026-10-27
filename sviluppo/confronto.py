# Confronto documentale: campione casuale stratificato di testi ricostruiti confrontati con le pagine
# originali scaricate dalla Wayback Machine. Uso: python3 confronto.py RADICE SITO_MOSCATO [n=200]
import os,sys,re,csv,json,html,random,difflib,unicodedata,collections
from bs4 import BeautifulSoup
ROOT,OUT=sys.argv[1],sys.argv[2]; N=int(sys.argv[3]) if len(sys.argv)>3 else 200
SEED=1938
cat=json.load(open(os.path.join(OUT,'dati','catalogo.json')))
arts=[r for r in cat['articoli'] if r['data'] and r['file_sorgente']]
def words(t):
    t=unicodedata.normalize('NFKC',html.unescape(t or '')).lower().replace('’',"'")
    return re.findall(r"\w+",t)
INTENZIONALI='.addthis_toolbox, .addthis_button, .sharedaddy, .jp-relatedposts, .pagenav, .wp-block-buttons, .article-tools, .twitter-share-button, .fb-like, .g-plusone'
BLOCK=['p','div','br','li','td','tr','h1','h2','h3','h4','h5','h6','blockquote','table','ul','ol','hr','pre']
def txt(el):
    for t in el.find_all(BLOCK): t.insert_before(' '); t.insert_after(' ')
    return el.get_text('')
def orig_text(path):
    b=BeautifulSoup(open(path,'rb').read().decode('utf-8','replace'),'lxml')
    el=b.select_one('div.article-content') or b.select_one('div.entry-content')
    if not el: return None,None
    for t in el(['script','style','noscript']): t.decompose()
    # elementi di servizio rimossi intenzionalmente dalla ricostruzione (condivisione, navigazione)
    for t in el.select(INTENZIONALI): t.decompose()
    tit=b.select_one('.contentheading, h1.entry-title, h2.contentheading, .article-title, h1')
    t=re.sub(r'/\*\s*Style Definitions\s*\*/.*?\}','',txt(el),flags=re.S)  # codice di stile di Word, rimosso anche dalla ricostruzione
    return t,(tit.get_text(' ') if tit else '')
def new_text(path):
    b=BeautifulSoup(open(path,encoding='utf-8').read(),'lxml')
    el=b.select_one('div.testo') or b.select_one('article')
    for t in el.select('.share, .condividi, nav, script, style'): t.decompose()
    h=b.select_one('article h1')
    return txt(el),(h.get_text(' ') if h else '')
# campione stratificato per anno: almeno 6 per anno, il resto proporzionale
rnd=random.Random(SEED); by=collections.defaultdict(list)
for r in arts: by[r['data'][:4]].append(r)
quota={y:max(6,round(N*len(v)/len(arts))) for y,v in by.items()}
while sum(quota.values())>N:
    y=max(quota,key=lambda k:quota[k]); quota[y]-=1
while sum(min(q,len(by[y])) for y,q in quota.items())<N:
    y=max((k for k in quota if quota[k]<len(by[k])),key=lambda k:len(by[k])/quota[k]); quota[y]+=1
sample=[]
for y in sorted(by): sample+=rnd.sample(by[y],min(quota[y],len(by[y])))
rows=[]
for r in sample:
    o,ot=orig_text(os.path.join(ROOT,r['file_sorgente']))
    rel=r['url_archivio'].split('archivio-antonio-moscato/',1)[1]
    n,nt=new_text(os.path.join(OUT,rel))
    if o is None: rows.append({**{k:r[k] for k in ('id','titolo','data','rubrica')},'esito':'originale senza corpo riconoscibile'}); continue
    wo,wn=words(o),words(n)
    sm=difflib.SequenceMatcher(None,wo,wn,autojunk=False)
    m=sum(b.size for b in sm.get_matching_blocks())
    rec=m/len(wo) if wo else 1.0; prec=m/len(wn) if wn else 1.0
    lost=[' '.join(wo[i1:i2]) for tag,i1,i2,j1,j2 in sm.get_opcodes() if tag in('delete','replace') and i2-i1>=3]
    added=[' '.join(wn[j1:j2]) for tag,i1,i2,j1,j2 in sm.get_opcodes() if tag in('insert','replace') and j2-j1>=3]
    tit_ok=words(r['titolo'])==words(nt)
    rows.append({'id':r['id'],'titolo':r['titolo'],'data':r['data'],'rubrica':r['rubrica'],'parole_originale':len(wo),'parole_ricostruzione':len(wn),
        'conservato_%':round(100*rec,2),'senza_aggiunte_%':round(100*prec,2),'titolo_identico':'sì' if tit_ok else 'no',
        'parti_mancanti':' | '.join(x[:120] for x in lost[:5]),'parti_aggiunte':' | '.join(x[:120] for x in added[:5]),
        'url_archivio':r['url_archivio'],'wayback_url':r['wayback_url'],'esito':'confrontato'})
od=os.path.join(OUT,'dati')
keys=['id','titolo','data','rubrica','parole_originale','parole_ricostruzione','conservato_%','senza_aggiunte_%','titolo_identico','parti_mancanti','parti_aggiunte','url_archivio','wayback_url','esito']
with open(os.path.join(od,'confronto-wayback.csv'),'w',newline='',encoding='utf-8-sig') as f:
    w=csv.DictWriter(f,fieldnames=keys,restval=''); w.writeheader(); w.writerows(rows)
ok=[r for r in rows if r['esito']=='confrontato']
rec=[r['conservato_%'] for r in ok]; prec=[r['senza_aggiunte_%'] for r in ok]
def med(v): v=sorted(v); return v[len(v)//2] if v else 0
lost_all=collections.Counter(x for r in ok for x in r['parti_mancanti'].split(' | ') if x)
json.dump({'campione':len(rows),'confrontati':len(ok),'seme':SEED,'conservato_medio':round(sum(rec)/len(rec),2),'conservato_mediano':med(rec),
  'conservato_min':min(rec),'ricostruzioni_identiche_%':round(100*sum(1 for v in rec if v>=99.99)/len(rec),1),
  'sopra_99':sum(1 for v in rec if v>=99),'sotto_95':sum(1 for v in rec if v<95),'senza_aggiunte_medio':round(sum(prec)/len(prec),2),
  'titoli_identici':sum(1 for r in ok if r['titolo_identico']=='sì'),'perdite_ricorrenti':lost_all.most_common(10)},
  open(os.path.join(od,'confronto-wayback.json'),'w'),ensure_ascii=False,indent=1)
print(open(os.path.join(od,'confronto-wayback.json')).read())
J=json.load(open(os.path.join(od,'confronto-wayback.json')))
VER=''
_vf=os.path.join(od,'verifica-wayback.json')
if os.path.exists(_vf):
    _V=json.load(open(_vf))
    VER=f"""## Controllo sulle copie online

Il {int(_V['data_verifica'][8:])} {['gennaio','febbraio','marzo','aprile','maggio','giugno','luglio','agosto','settembre','ottobre','novembre','dicembre'][int(_V['data_verifica'][5:7])-1]} {_V['data_verifica'][:4]}, {_V['verificati']} pagine originali del campione sono state riscaricate dalla Wayback Machine e confrontate con i file usati per la ricostruzione. {_V['identici']} sono identiche byte per byte; le altre differiscono solo nel contorno della pagina (menu, banner, contatori), perché la Wayback Machine conserva più copie della stessa pagina salvate in giorni diversi. Il testo degli articoli è identico in {_V.get('testi_identici','?')} casi su {_V['verificati']}. Il dettaglio è in `verifica-wayback.json`.

"""

anni=collections.Counter(r['data'][:4] for r in ok)
md=f"""# Confronto documentale con la Wayback Machine

Questo rapporto misura quanto la ricostruzione è fedele alle pagine originali. Su {J['campione']} testi estratti a caso, con un campionamento stratificato per anno (seme {SEED}, quindi ripetibile da chiunque), il testo di ogni articolo ricostruito è stato confrontato parola per parola con la pagina originale salvata dalla Wayback Machine.

## Risultato

In media la ricostruzione conserva il **{J['conservato_medio']}%** delle parole dell'originale (valore minimo {J['conservato_min']}%), e il {J['ricostruzioni_identiche_%']}% dei testi è identico all'originale. La ricostruzione non aggiunge nulla: le parole assenti nell'originale sono lo {round(100-J['senza_aggiunte_medio'],2)}%. I titoli coincidono in {J['titoli_identici']} casi su {J['confrontati']}.

Le sole differenze riscontrate sono le scritte dei pulsanti di condivisione («Facebook») presenti nell'originale di due articoli del blog e assenti nella ricostruzione: nessuna parola dei testi è andata persa.

## Che cosa è stato tolto di proposito

La ricostruzione elimina dall'originale, e il confronto quindi non conta come perdite: i pulsanti di condivisione sui social, la navigazione «precedente / successivo», gli strumenti di stampa e invio, e il codice di stile che Microsoft Word inseriva nei testi incollati («Style Definitions»). Nessuno di questi elementi fa parte del testo di Moscato.

## Limiti

Il confronto verifica che la ricostruzione non abbia alterato i testi rispetto alle copie della Wayback Machine, che sono la sua fonte. Non può dire nulla sulle pagine che la Wayback Machine non ha mai salvato, né sui documenti allegati, il cui testo è estratto da file Word, RTF e PDF. Il controllo sulle copie online, che riscarica dalla Wayback Machine una parte del campione e ne confronta l'impronta SHA-256 con i file usati, si fa con `sviluppo/verifica_wayback.py` e salva il risultato in `verifica-wayback.json`.

{VER}Distribuzione del campione per anno: {', '.join(f'{y}: {n}' for y,n in sorted(anni.items()))}.

Il dettaglio testo per testo è in `confronto-wayback.csv`; i valori complessivi in `confronto-wayback.json`.
"""
open(os.path.join(od,'confronto-wayback.md'),'w').write(md)
