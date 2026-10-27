# Manifesto di integrità: impronta SHA-256, dimensione e stato di ogni file del sito.
# Uso: python3 integrita.py SITO_MOSCATO   (alla fine della costruzione)
# Verifica (macOS/Linux): cd SITO_MOSCATO && shasum -a 256 -c SHA256SUMS
import os,sys,csv,json,hashlib
OUT=sys.argv[1]
SKIP_DIRS={'.git'}; SKIP={'SHA256SUMS','dati/manifesto-integrita.csv','.DS_Store'}
cat=json.load(open(os.path.join(OUT,'dati','catalogo.json')))
st={}
for r in cat['documenti']:
    u=r['url_archivio'].split('archivio-antonio-moscato/',1)[-1]
    if u: st[u]=r['stato']
    if r.get('file_archivio'): st[r['file_archivio']]=r['stato']
def stato(p):
    if p in st: return st[p]
    if p.startswith('documenti/file/'): return st.get(p,'recuperato')
    if p.startswith('articoli/'): return 'reindirizzamento (doppione o pagina di servizio)' if p[9:-5] in REDIR else 'testo recuperato (ripulito)'
    if p.startswith('documenti/testo/'): return 'testo estratto dal documento'
    if p.startswith('sviluppo/'): return 'codice di ricostruzione'
    if p.startswith('assets/img/'): return 'immagine recuperata'
    if p.startswith('dati/'): return 'metadati'
    return 'pagina o risorsa generata'
REDIR={'67','273','272','25','235','119','1946','2033','2040','2264','2020','2279'}
rows=[]
for d,dirs,files in os.walk(OUT):
    dirs[:]=sorted(x for x in dirs if x not in SKIP_DIRS and x!='__pycache__')
    for f in sorted(files):
        full=os.path.join(d,f); p=os.path.relpath(full,OUT).replace(os.sep,'/')
        if p in SKIP or f=='.DS_Store': continue
        h=hashlib.sha256()
        with open(full,'rb') as fh:
            for b in iter(lambda: fh.read(1<<20),b''): h.update(b)
        rows.append((p,h.hexdigest(),os.path.getsize(full),stato(p)))
with open(os.path.join(OUT,'SHA256SUMS'),'w') as f:
    for p,h,_,_ in rows: f.write(f'{h}  {p}\n')
with open(os.path.join(OUT,'dati','manifesto-integrita.csv'),'w',newline='',encoding='utf-8-sig') as f:
    w=csv.writer(f); w.writerow(['percorso','sha256','dimensione_byte','stato']); w.writerows(rows)
from collections import Counter
print('integrita',len(rows),'file',sum(r[2] for r in rows),'byte',Counter(r[3] for r in rows).most_common())
