# Controllo a campione sulle copie online: riscarica dalla Wayback Machine le pagine originali
# di 30 testi del campione e verifica che siano identiche (SHA-256) ai file usati per la ricostruzione.
# Uso (dal Mac, serve internet): python3 sviluppo/verifica_wayback.py   [dalla cartella antoniomoscato]
import os,sys,csv,json,hashlib,time,urllib.request,datetime
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE); OUT=os.path.join(ROOT,'SITO_MOSCATO')
cat={r['id']:r for r in json.load(open(os.path.join(OUT,'dati','catalogo.json')))['articoli']}
camp=[r for r in csv.DictReader(open(os.path.join(OUT,'dati','confronto-wayback.csv'),encoding='utf-8-sig'))][::7][:30]
res=[]
for i,c in enumerate(camp,1):
    r=cat[c['id']]; ts=r['wayback_timestamp']; url=r['url_originale']
    raw=f'https://web.archive.org/web/{ts}id_/{url}'
    loc=hashlib.sha256(open(os.path.join(ROOT,r['file_sorgente']),'rb').read()).hexdigest()
    try:
        req=urllib.request.Request(raw,headers={'User-Agent':'archivio-antonio-moscato verifica'})
        data=urllib.request.urlopen(req,timeout=60).read(); rem=hashlib.sha256(data).hexdigest()
        os.makedirs(os.path.join(ROOT,'verifica_cache'),exist_ok=True); open(os.path.join(ROOT,'verifica_cache',r['id']+'.html'),'wb').write(data)
        esito='identico' if rem==loc else 'diverso'
    except Exception as e: rem='';esito='errore: '+str(e)[:80]
    print(f'{i:2}/{len(camp)} {esito:9} {r["titolo"][:60]}',flush=True)
    res.append({'id':r['id'],'titolo':r['titolo'],'wayback':raw,'sha256_locale':loc,'sha256_wayback':rem,'esito':esito})
    time.sleep(2)
ok=sum(1 for x in res if x['esito']=='identico')
json.dump({'data_verifica':datetime.date.today().isoformat(),'verificati':len(res),'identici':ok,'risultati':res},
          open(os.path.join(OUT,'dati','verifica-wayback.json'),'w'),ensure_ascii=False,indent=1)
print(f'\nFile identici byte per byte: {ok} su {len(res)}. Copie scaricate in verifica_cache/ per il confronto del testo.')
