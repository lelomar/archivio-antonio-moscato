# Catalogo dei metadati esportabile: CSV, JSON e Dublin Core (OAI-DC) per ogni testo e documento.
import os,re,csv,json,html,datetime
from xml.sax.saxutils import escape as xesc
BASE='https://lelomar.github.io/archivio-antonio-moscato/'
WB='https://web.archive.org/web/'
def _norm(u):
    u=html.unescape(u or '').strip()
    u=re.sub(r'^https?://','',u,flags=re.I); u=re.sub(r'^www\.','',u,flags=re.I)
    u=re.sub(r'^antoniomoscato\.altervista\.org(:80|:443)?','antoniomoscato.altervista.org',u,flags=re.I)
    u=re.sub(r'[&?]doing_wp_cron=[0-9.]+','',u)
    return u.rstrip('/').lower()
def _cdx(root):
    idx={}
    for row in json.load(open(os.path.join(root,'.cdx.json'))):
        if not isinstance(row,list) or len(row)<2 or not str(row[0]).isdigit(): continue
        idx.setdefault(_norm(row[1]),set()).add(row[0])
    return idx
def provenienza(root,work,arts):
    """Indirizzo originale e copia della Wayback Machine usata, per ogni articolo."""
    mp=json.load(open(os.path.join(work,'map.json'))); idx=_cdx(root); out={}
    for a in arts:
        if str(a['id']).startswith('wp-'): urls=['https://antoniomoscato.altervista.org/'+(a.get('slug') or '')+'/']; cut=None
        else: urls=list(mp.get(a.get('src') or '',[])) or [f"http://antoniomoscato.altervista.org/index.php?option=com_content&view=article&id={a['id']}"]; cut='20211101'
        cand=[(t,u) for u in urls for t in (idx.get(_norm(u)) or {''})]
        if cut and any(c[0] and c[0]<cut for c in cand): cand=[c for c in cand if c[0] and c[0]<cut]
        cand=[c for c in cand if c[0]] or [('',urls[0])]
        ts,u=max(cand); out[str(a['id'])]=(html.unescape(u),ts)
    return out
def run(OUT,root,work,arts,docs,catname,dmname,kwname):
    mp=json.load(open(os.path.join(work,'map.json')))
    idx=_cdx(root)
    rap={}
    rp=os.path.join(root,'recupero','rapporto.json')
    if os.path.exists(rp): rap=json.load(open(rp))
    def best(urls,cut=None):
        cand=[(t,u) for u in urls for t in (idx.get(_norm(u)) or {''})]
        # dal novembre 2021 i vecchi indirizzi Joomla rimandano alla home del nuovo blog: si usa l'ultima copia precedente
        if cut and any(c[0] and c[0]<cut for c in cand): cand=[c for c in cand if c[0] and c[0]<cut]
        cand=[c for c in cand if c[0]] or [('',urls[0])] if urls else [('','')]
        ts,u=max(cand)
        return u,ts
    AUTF={str(a['id']):a for a in arts}
    NOTA=''
    rows_a=[]
    for a in sorted(arts,key=lambda a:(a['date'] or '',str(a['id']))):
        src=a.get('src') or ''
        if str(a['id']).startswith('wp-'):
            urls=['https://antoniomoscato.altervista.org/'+(a.get('slug') or '')+'/']
        else:
            urls=[u for u in mp.get(src,[])] or [f"http://antoniomoscato.altervista.org/index.php?option=com_content&view=article&id={a['id']}"]
        u,ts=best(urls,None if str(a['id']).startswith('wp-') else '20211101')
        rows_a.append({'id':str(a['id']),'tipo':'articolo','titolo':a['title'],'autore':a.get('autore',''),'nota_autore':a.get('mosc',''),'attribuzione':a.get('cert',''),'data_scrittura':a.get('scritto',''),'data':a['date'] or '',
            'rubrica':catname(a['catid']),'lingua':a.get('lang','it'),'temi':'; '.join(kwname(k) for k in a.get('kws',[])),
            'url_archivio':BASE+f"articoli/{a['id']}.html",'url_originale':html.unescape(u),'wayback_timestamp':ts,
            'wayback_url':(WB+ts+'/'+html.unescape(u)) if ts else '','file_sorgente':src})
    rows_d=[]
    for g,d in sorted(docs.items()):
        r=rap.get(str(g)) or {}
        # stato del file e modo del recupero sono due informazioni distinte
        if d.get('out') and d.get('broken'): stato='incompleto (troncato a 1 MB)'
        elif d.get('out'): stato='integro'
        elif dmname(d.get('cat',0))=='Audio e video': stato='audio/video non archiviato'
        else: stato='mancante'
        recupero=('recupero mirato (dopo la prima ricostruzione)' if r.get('file') else 'prima ricostruzione') if d.get('out') else ''
        orig=f"http://antoniomoscato.altervista.org/index.php?option=com_docman&task=doc_download&gid={g}&Itemid=2"
        if r.get('from'):
            m=re.match(r'https://web\.archive\.org/web/(\d+)/(.*)',r['from']); ts,u=(m.group(1),m.group(2)) if m else ('',orig)
        else:
            urls=mp.get(d.get('file') or '',[])+[orig]; u,ts=best(urls,'20211101')
        page=d.get('page') or d.get('out') or ''
        ext=(d.get('out') or '').rsplit('.',1)[-1].upper() if d.get('out') else ''
        rows_d.append({'id':f'd{g}','tipo':'documento','titolo':(d.get('title') or d.get('filename') or '').replace(' hot!',''),'autore':'','nota_autore':'','attribuzione':'da verificare',
            'data':d.get('iso','') or '','rubrica':dmname(d.get('cat',0)),'lingua':d.get('lang','it'),'formato':ext,'stato':stato,'recupero':recupero,
            'dimensione_byte':d.get('size','') or '','nome_file_originale':d.get('filename') or '','file_archivio':d.get('out') or '',
            'url_archivio':(BASE+page) if page else '','url_originale':html.unescape(u),'wayback_timestamp':ts,
            'wayback_url':(WB+ts+'/'+html.unescape(u)) if ts else ''})
    od=os.path.join(OUT,'dati'); os.makedirs(od,exist_ok=True)
    for name,rows in (('catalogo-articoli.csv',rows_a),('catalogo-documenti.csv',rows_d)):
        with open(os.path.join(od,name),'w',newline='',encoding='utf-8-sig') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    head={'titolo':'Movimento operaio. Il sito di Antonio Moscato (2009–2021), ricostruito. Catalogo','curatore':'Leonardo Lomartire','doi':'10.5281/zenodo.23670900',
          'wikidata':'https://www.wikidata.org/wiki/Q141880166','licenza':'CC BY-NC-SA 4.0','generato':datetime.date.today().isoformat(),
          'note':'wayback_timestamp indica la copia della Wayback Machine più recente disponibile per l’URL originale.','articoli':len(rows_a),'documenti':len(rows_d)}
    json.dump({'meta':head,'articoli':rows_a,'documenti':rows_d},open(os.path.join(od,'catalogo.json'),'w'),ensure_ascii=False,indent=1)
    X=['<?xml version="1.0" encoding="UTF-8"?>','<records xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/" xmlns:dc="http://purl.org/dc/elements/1.1/">']
    for r in rows_a+rows_d:
        X.append('<oai_dc:dc>'+''.join(f'<dc:{k}>{xesc(str(v))}</dc:{k}>' for k,v in [('identifier',r['url_archivio']),('title',r['titolo']),('creator',r['autore']),('date',r['data']),('type','Text'),('language',r['lingua']),('subject',r['rubrica'])]+[('subject',t) for t in r.get('temi','').split('; ') if t]+[('format',r.get('formato',''))]*bool(r.get('formato'))+[('source',r['url_originale']),('relation','https://doi.org/10.5281/zenodo.23670900'),('publisher','Movimento operaio – La pagina di Antonio Moscato (antoniomoscato.altervista.org)'),('rights','Testi di Antonio Moscato e degli autori indicati; schede: CC BY-NC-SA 4.0')] if v)+'</oai_dc:dc>')
    X.append('</records>')
    open(os.path.join(od,'catalogo-dc.xml'),'w').write('\n'.join(X))
    from collections import Counter
    return len(rows_a),len(rows_d),sum(1 for r in rows_a if r['wayback_timestamp']),Counter(r['stato'] for r in rows_d)
