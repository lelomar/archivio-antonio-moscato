# Estrae i link esterni dagli articoli ricostruiti, con la data del primo articolo che li cita.
# Uso: python3 estrai_link.py SITO_MOSCATO  -> sviluppo/link_esterni.json
import os,re,sys,json,glob,html,urllib.parse
OUT=sys.argv[1]; HERE=os.path.dirname(os.path.abspath(__file__))
cat={r['id']:r for r in json.load(open(os.path.join(OUT,'dati','catalogo.json')))['articoli']}
SCARTA=('mail.yahoo.com','mail.google.com','localhost','127.0.0.1','webmail','mail.live.com','outlook.live.com','.mail.')
L={}
for f in sorted(glob.glob(os.path.join(OUT,'articoli','*.html'))):
    aid=os.path.basename(f)[:-5]
    if aid not in cat: continue
    s=open(f,encoding='utf-8').read()
    m=re.search(r'<div class="testo"[^>]*>(.*?)</div>\s*<p class="orig"',s,re.S)
    if not m: continue
    for u in re.findall(r'<a [^>]*href="(https?://[^"]+)"',m.group(1)):
        u=html.unescape(u).strip(); h=urllib.parse.urlsplit(u).netloc.lower()
        if not h or 'archive.org' in h or 'antoniomoscato' in h or any(x in h for x in SCARTA): continue
        e=L.setdefault(u,{'articoli':[],'data':''})
        if aid not in e['articoli']: e['articoli'].append(aid)
        d=cat[aid]['data']
        if d and (not e['data'] or d<e['data']): e['data']=d
json.dump(L,open(os.path.join(HERE,'link_esterni.json'),'w'),ensure_ascii=False,indent=0)
print('link unici',len(L),'senza data',sum(1 for v in L.values() if not v['data']))
