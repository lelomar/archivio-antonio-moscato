# Cerca nella Wayback Machine, per ogni link esterno degli articoli, la copia più vicina alla data
# in cui Moscato lo ha citato. Si può interrompere (ctrl-C) e rilanciare: riprende da dove era arrivato.
# Uso (dal Mac, serve internet): python3 sviluppo/cerca_link_wayback.py   [dalla cartella antoniomoscato]
import os,sys,json,time,urllib.request,urllib.parse,datetime
HERE=os.path.dirname(os.path.abspath(__file__))
L=json.load(open(os.path.join(HERE,'link_esterni.json')))
OUTF=os.path.join(HERE,'link_wayback.json')
R=json.load(open(OUTF)) if os.path.exists(OUTF) else {}
todo=[u for u in L if u not in R or R[u].get('stato')=='errore']
print(f'Link da cercare: {len(todo)} su {len(L)} (gli altri sono già fatti).',flush=True)
def save(): json.dump(R,open(OUTF+'.tmp','w'),ensure_ascii=False); os.replace(OUTF+'.tmp',OUTF)
def query(u,ts):
    q=urllib.parse.urlencode({'url':u,'output':'json','fl':'timestamp,statuscode,mimetype','filter':'statuscode:200','sort':'closest','closest':ts,'limit':'3'})
    req=urllib.request.Request('https://web.archive.org/cdx/search/cdx?'+q,headers={'User-Agent':'archivio-antonio-moscato (ricerca link storici)'})
    return json.loads(urllib.request.urlopen(req,timeout=60).read() or b'[]')
import threading
from concurrent.futures import ThreadPoolExecutor
LOCK=threading.Lock(); PAUSA=[0.3]; t0=time.time(); fatti=[0]
def lavora(u):
    ts=L[u]['data'].replace('-','')
    for tent in range(5):
        try:
            rows=query(u,ts); rows=rows[1:] if rows and rows[0][0]=='timestamp' else rows
            if rows:
                best=rows[0][0]
                giorni=abs((datetime.date(int(best[:4]),int(best[4:6]),int(best[6:8]))-datetime.date(int(ts[:4]),int(ts[4:6]),int(ts[6:8]))).days)
                r={'stato':'archiviato','timestamp':best,'giorni_dalla_citazione':giorni,'mimetype':rows[0][2]}
            else: r={'stato':'non archiviato'}
            break
        except urllib.error.HTTPError as e:
            if e.code in (429,503,502,504):
                w=60*(tent+1); print(f'  la Wayback chiede una pausa ({e.code}): attendo {w} secondi',flush=True); time.sleep(w); PAUSA[0]=min(PAUSA[0]*1.5,3)
            else: r={'stato':'errore','errore':str(e)[:80]}; break
        except Exception as e:
            r={'stato':'errore','errore':str(e)[:80]}; time.sleep(10)
    with LOCK:
        R[u]=r; fatti[0]+=1; i=fatti[0]
        if i%25==0 or i==len(todo):
            save(); el=time.time()-t0; ok=sum(1 for v in R.values() if v.get('stato')=='archiviato')
            print(f'{i}/{len(todo)} · archiviati finora {ok} · mancano circa {int(el/i*(len(todo)-i)/60)} minuti',flush=True)
    time.sleep(PAUSA[0])
with ThreadPoolExecutor(max_workers=4) as ex: list(ex.map(lavora,todo))
save()
from collections import Counter
print('\nFinito:',dict(Counter(v['stato'] for v in R.values())),'· risultati in sviluppo/link_wayback.json')
