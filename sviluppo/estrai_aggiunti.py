# Testi del sito originale che l'estrazione automatica (extract.py) non ha riconosciuto, recuperati in un secondo
# momento dalle stesse copie della Wayback Machine. Ogni testo è estratto da un file preciso della cartella
# scaricata, senza modificarne le parole; il risultato (testi_aggiunti.json) entra nella costruzione come gli altri.
# Uso: python3 sviluppo/estrai_aggiunti.py [cartella antoniomoscato]
import os,sys,json,hashlib
from bs4 import BeautifulSoup
ROOT=sys.argv[1] if len(sys.argv)>1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE=os.path.dirname(os.path.abspath(__file__))
AGGIUNTI=[
 # L'articolo 12, «Benvenuti!», categoria homepage del sito Joomla: la lettera di benvenuto firmata da Moscato
 # (Recanati, 1 febbraio 2016). La pagina non ha l'intestazione standard degli articoli (.contentheading),
 # per questo extract.py non l'aveva estratta.
 {'id':'12','file':'index__q13a2169bf0de.php','title':'Benvenuti!','catid':'2','catslug':'homepage','slug':'benvenuti',
  # data di creazione dell'articolo: la pagina Joomla non la mostra; è conservata nei metadati della stessa pagina
  # importata nel blog WordPress del sito (benvenuti/index.html, article:published_time)
  'date_da':('benvenuti/index.html','article:published_time'),
  'inizio':'BENVENUTI!','autore':'Antonio Moscato','fonte_autore':'firma in calce («Antonio Moscato, Recanati 1 febbraio 2016»)'},
]
out=[]
for t in AGGIUNTI:
    p=os.path.join(ROOT,t['file']); raw=open(p,'rb').read()
    soup=BeautifulSoup(raw.decode('utf-8','ignore'),'lxml')
    kw=(soup.find('meta',attrs={'name':'keywords'}) or {}).get('content','')
    cont=soup.select_one('.article-content')
    # il testo comincia dal titolo «BENVENUTI!»: ciò che precede sono i pulsanti di condivisione e l'intestazione
    # vuota del modulo «Ultimi articoli inseriti», che il sito riempiva con un elenco automatico
    start=[d for d in cont.find_all('div',class_='module_red') if d.get_text(strip=True)==t['inizio']][0]
    parts=[]
    for el in start.find_next_siblings():
        if el.name=='div' and el.get('style','').startswith('float:right'): break   # pulsanti di condivisione finali
        parts.append(str(el))
    d=''
    if t.get('date_da'):
        f,prop=t['date_da']; s2=BeautifulSoup(open(os.path.join(ROOT,f),encoding='utf-8',errors='ignore').read(),'lxml')
        m=s2.find('meta',attrs={'property':prop}); d=(m.get('content','') if m else '')[:10]
    out.append({'id':t['id'],'title':t['title'],'date':d,'catid':t['catid'],'catslug':t['catslug'],'slug':t['slug'],
                'src':t['file'],'kw':kw,'html':'\n'.join(parts),'autore':t['autore'],'fonte_autore':t['fonte_autore'],
                'sha256_file':hashlib.sha256(raw).hexdigest(),'nota':'recuperato dopo la prima ricostruzione (estrai_aggiunti.py)'})
json.dump(out,open(os.path.join(HERE,'testi_aggiunti.json'),'w'),ensure_ascii=False,indent=1)
print('testi aggiunti:',[(x['id'],x['title'],x['date'],len(x['html'])) for x in out])
