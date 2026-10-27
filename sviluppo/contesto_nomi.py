# Verifica contestuale dei temi formati da un solo nome (cognome o nome proprio) che potrebbero
# coincidere con un tema a nome completo: per ogni articolo etichettato con il nome breve, cerca nel
# testo quali nomi completi compaiono. Uso: python3 contesto_nomi.py SITO_MOSCATO > risultato.json
import sys,os,re,json,csv,glob,unicodedata,collections
OUT=sys.argv[1]
def norm(t):
    t=unicodedata.normalize('NFKD',(t or '').lower()); t=''.join(c for c in t if not unicodedata.combining(c))
    return re.sub(r'\s+',' ',re.sub(r'[^a-z0-9ñ]+',' ',t)).strip()
voc=list(csv.DictReader(open(os.path.join(OUT,'dati','vocabolario-temi.csv'),encoding='utf-8-sig')))
lab2k={v['etichetta']:v['chiave'] for v in voc}; N={v['chiave']:int(v['testi']) for v in voc}; E={v['chiave']:v['etichetta'] for v in voc}
T={}
for f in sorted(glob.glob(os.path.join(OUT,'assets','testi-*.js'))):
    s=open(f,encoding='utf-8').read(); s=s[s.index('||{},{')+5:s.rindex('}')+1]
    T.update(json.loads(s))
arts=list(csv.DictReader(open(os.path.join(OUT,'dati','catalogo-articoli.csv'),encoding='utf-8-sig')))
tag=collections.defaultdict(list)
for a in arts:
    for t in [x for x in a['temi'].split('; ') if x]:
        if t in lab2k: tag[lab2k[t]].append(a['id'])
keys=set(N)
cand={}
for k in keys:
    if len(k.split())!=1: continue
    full=[x for x in keys if len(x.split()) in (2,3) and (x.split()[-1]==k or x.split()[0]==k) and x!=k]
    if full: cand[k]=full
res={}
for k,full in cand.items():
    per=[]
    for aid in tag[k]:
        tx=norm(T.get(aid,''))
        hit=[f for f in full if re.search(r'\b'+re.escape(f)+r'\b',tx)]
        per.append(hit)
    c=collections.Counter(tuple(h) for h in per)
    res[k]={'etichetta':E[k],'testi':N[k],'nomi_completi':{f:E[f] for f in full},'articoli':len(per),
            'trovati':{(' + '.join(E[x] for x in h) if h else 'nessuno'):n for h,n in c.most_common()}}
json.dump(res,sys.stdout,ensure_ascii=False,indent=1)
