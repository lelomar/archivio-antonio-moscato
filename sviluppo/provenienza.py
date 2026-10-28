# Modello della provenienza a livelli. Ogni testo dell'archivio è descritto come una catena di oggetti distinti,
# ciascuno con identificativo, impronta e relazione esplicita con quello da cui deriva:
#   .o originale (la pubblicazione sul sito di Moscato)  -> .c cattura (la copia della Wayback Machine usata)
#   -> .t testo estratto o convertito  -> .e edizione (la pagina HTML di questo archivio)
#   più gli interventi (.i1, .i2, …): eventi che hanno modificato qualcosa fra un livello e l'altro.
# Corrispondenze: PREMIS (oggetti/eventi/agenti), PROV-O (wasDerivedFrom, wasGeneratedBy), Dublin Core (source).
# Scrive dati/provenienza.json, dati/provenienza.csv, dati/eventi.csv.
import os,re,csv,json,hashlib,datetime
BASE='https://lelomar.github.io/archivio-antonio-moscato/'
def _sha(b): return hashlib.sha256(b).hexdigest()
def _fsha(p):
    if not p or not os.path.isfile(p): return '',''
    with open(p,'rb') as f: b=f.read()
    return _sha(b),len(b)
def _testo(s):
    m=re.search(r'<div class="testo"[^>]*>(.*?)</div>\s*(?:<section class="scheda"|<div class="segnala"|<p class="orig")',s,re.S)
    return m.group(1) if m else ''
def conta_link(body):
    """Conta gli interventi sui collegamenti nel corpo di un articolo già pubblicato."""
    c=dict(interni=0,wayback_interni=0,esterni_archiviati=0,esterni_non_archiviati=0)
    for t in re.findall(r'<a\s[^>]*>',body):
        if 'class="lx"' in t: c['esterni_archiviati']+=1
        elif 'class="lx-na"' in t: c['esterni_non_archiviati']+=1
        elif re.search(r'href="(\.\./)+(articoli|categorie|documenti|temi|anni|cerca)',t): c['interni']+=1
        elif 'web.archive.org/web/' in t and 'antoniomoscato' in t: c['wayback_interni']+=1
    c['immagini']=len(re.findall(r'<img[^>]+src="(\.\./)+assets/img/',body))
    c['note']=len(re.findall(r'<a\s[^>]*href="#[^"]+"',body))
    return c
def run(OUT,root,WORK,arts,docs,dmname,DUP_ART):
    oggi=datetime.date.today().isoformat()
    zj=os.path.join(OUT,'.zenodo.json')
    ver=json.load(open(zj)).get('version','') if os.path.exists(zj) else ''
    cat=json.load(open(os.path.join(OUT,'dati','catalogo.json')))
    CA={r['id']:r for r in cat['articoli']}; CD={r['id']:r for r in cat['documenti']}
    rap=os.path.join(root,'recupero','rapporto.json'); rap=json.load(open(rap)) if os.path.exists(rap) else {}
    dup_in={}
    for k,v in DUP_ART.items(): dup_in.setdefault(str(v),[]).append(str(k))
    oggetti=[]; eventi=[]; righe=[]
    def ev(eid,oid,da,a,tipo,descr,q='',agente='programma di ricostruzione'):
        eventi.append({'id_evento':eid,'oggetto':oid,'da_livello':da,'a_livello':a,'tipo':tipo,'descrizione':descr,'quantita':q,'agente':agente,'data':oggi})
        return eid
    _agf=os.path.join(WORK,'testi_aggiunti.json'); AGG={t['id']:t for t in json.load(open(_agf,encoding='utf-8'))} if os.path.exists(_agf) else {}
    for a in arts:
        i=str(a['id']); oid='AM-'+i; r=CA.get(i,{})
        csha,cby=_fsha(os.path.join(root,a['src'])) if a.get('src') else ('','')
        ef=os.path.join(OUT,'articoli',i+'.html'); esha,eby=_fsha(ef)
        body=_testo(open(ef,encoding='utf-8').read()) if os.path.exists(ef) else ''
        lk=conta_link(body); plain=a.get('plain','')
        wp=i.startswith('wp-')
        L={'originale':{'id':oid+'.o','descrizione':'articolo pubblicato sul sito antoniomoscato.altervista.org',
                'url':r.get('url_originale',''),'sistema':'WordPress (blog 2018-2021)' if wp else 'Joomla, componente com_content',
                'data_pubblicazione':a.get('date') or '','autore':a.get('autore',''),'attribuzione':a.get('cert','')},
           'cattura':{'id':oid+'.c','deriva_da':oid+'.o','relazione':'copia di','descrizione':'copia della pagina conservata dalla Wayback Machine',
                'wayback_timestamp':r.get('wayback_timestamp',''),'wayback_url':r.get('wayback_url',''),'file_scaricato':a.get('src') or '','sha256':csha,'byte':cby},
           'testo':{'id':oid+'.t','deriva_da':oid+'.c','relazione':'estratto da',
                'metodo':'estrazione del corpo dell’articolo dalla pagina (extract.py) e pulizia del codice (build.py)',
                'sha256_testo_semplice':_sha(plain.encode('utf-8')) if plain else '','parole':len(plain.split()),'lingua':a.get('lang','it')},
           'edizione':{'id':oid+'.e','deriva_da':oid+'.t','relazione':'edizione di','descrizione':'pagina HTML dell’archivio ricostruito','versione':ver,
                'url':BASE+f'articoli/{i}.html','file':f'articoli/{i}.html','sha256':esha,'byte':eby}}
        I=[]
        def add(*x,**k): I.append(ev(f'{oid}.i{len(I)+1}',oid,*x,**k))
        if i in AGG:
            add('cattura','testo','recupero mirato','testo non riconosciuto dalla prima estrazione e recuperato in seguito dalla stessa copia (estrai_aggiunti.py); escluse l’intestazione vuota del modulo «Ultimi articoli inseriti» e i pulsanti di condivisione',agente='programma di recupero (estrai_aggiunti.py)')
            if AGG[i].get('date'): add('originale','edizione','data di pubblicazione','data di creazione dell’articolo ricavata dai metadati della stessa pagina importata nel blog WordPress del sito (article:published_time)',agente='programma di recupero (estrai_aggiunti.py)')
        add('cattura','testo','pulizia','rimossi menu, script, pulsanti di condivisione, stili di Word e link a file locali; il testo non è stato modificato')
        if lk['interni']: add('testo','edizione','link interni','collegamenti al vecchio sito ricondotti alle pagine di questo archivio',lk['interni'])
        if lk['wayback_interni']: add('testo','edizione','link interni non recuperati','collegamenti a pagine del vecchio sito non conservate, indirizzati alla Wayback Machine',lk['wayback_interni'])
        if lk['esterni_archiviati']: add('testo','edizione','link esterni archiviati','collegamenti a siti esterni indirizzati alla copia della Wayback Machine più vicina alla data della citazione; indirizzo originale conservato',lk['esterni_archiviati'])
        if lk['esterni_non_archiviati']: add('testo','edizione','link esterni non archiviati','collegamenti a siti esterni senza copia d’archivio, lasciati all’indirizzo originale e segnalati',lk['esterni_non_archiviati'])
        if lk['immagini']: add('cattura','edizione','immagini','immagini recuperate dalla Wayback Machine e incluse nell’archivio',lk['immagini'])
        if lk['note']: add('testo','edizione','note','rimandi interni (note e indici) resi funzionanti',lk['note'])
        cert=a.get('cert','')
        add('testo','edizione','attribuzione',f"autore indicato: {a.get('autore') or 'non identificato'}; certezza: {cert}"+(f"; {a.get('mosc')}" if a.get('mosc') else ''),
            agente='segnalazione verificata dal curatore' if cert=='verificata' else 'programma di attribuzione (autori2.py)'+(', da verificare' if cert in ('media','bassa') else ''))
        if a.get('scritto'): add('testo','edizione','data di scrittura',f"data di scrittura ricavata dal testo: {a['scritto']}",agente='programma di datazione (date2.py)')
        for d in dup_in.get(i,[]): add('originale','edizione','doppione unito',f'l’articolo AM-{d}, pubblicato due volte sul sito, rinvia a questa pagina')
        oggetti.append({'id':oid,'tipo':'articolo','titolo':a['title'],'stato':'integro','livelli':L,'interventi':I})
        righe.append({'id':oid,'tipo':'articolo','titolo':a['title'],'stato':'integro',
            'originale_url':L['originale']['url'],'originale_data':L['originale']['data_pubblicazione'],
            'cattura_timestamp':L['cattura']['wayback_timestamp'],'cattura_url':L['cattura']['wayback_url'],'cattura_file':L['cattura']['file_scaricato'],'cattura_sha256':csha,
            'testo_metodo':'estrazione HTML','testo_sha256':L['testo']['sha256_testo_semplice'],'testo_parole':L['testo']['parole'],
            'edizione_file':L['edizione']['file'],'edizione_sha256':esha,'edizione_versione':ver,'interventi':len(I)})
    for g,d in sorted(docs.items()):
        oid=f'AM-d{g}'; r=CD.get(f'd{g}',{}); rp=rap.get(str(g)) or {}
        nome=d.get('out') or d.get('filename') or ''
        ext=nome.rsplit('.',1)[-1].lower() if '.' in nome else ''
        L={'originale':{'id':oid+'.o','descrizione':'documento offerto in download nella sezione «I grandi nodi del Novecento» (DOCman)',
                'url':r.get('url_originale',''),'sistema':'Joomla, componente DOCman','nome_file':d.get('filename') or '','data_pubblicazione':d.get('iso','')}}
        I=[]
        def add(*x,**k): I.append(ev(f'{oid}.i{len(I)+1}',oid,*x,**k))
        stato=r.get('stato','')
        if d.get('out'):
            fsha,fby=_fsha(os.path.join(OUT,d['out']))
            L['cattura']={'id':oid+'.c','deriva_da':oid+'.o','relazione':'copia di','descrizione':'file originale conservato dalla Wayback Machine',
                'wayback_timestamp':r.get('wayback_timestamp',''),'wayback_url':r.get('wayback_url',''),'file':d['out'],'sha256':fsha,'byte':fby,
                'formato':ext.upper(),'integro':not d.get('broken')}
            if rp.get('file'): add('originale','cattura','recupero mirato','file ritrovato interrogando tutte le copie del link di download, dopo la prima ricostruzione',agente='programma di recupero (recupera.py)')
            if d.get('broken'): add('originale','cattura','troncamento','il file è stato salvato solo fino al primo megabyte (1.048.576 byte): il testo è incompleto',agente='Wayback Machine, al momento dell’archiviazione')
            if d.get('page'):
                t=d.get('text','')
                L['testo']={'id':oid+'.t','deriva_da':oid+'.c','relazione':'convertito da',
                    'metodo':'pdftotext (Poppler), paragrafi ricomposti' if ext=='pdf' else 'LibreOffice, conversione in HTML e pulizia del codice',
                    'sha256_testo_semplice':_sha(t.encode('utf-8')) if t else '','parole':len(t.split()),'lingua':d.get('lang','it')}
                add('cattura','testo','conversione',L['testo']['metodo'])
                esha,eby=_fsha(os.path.join(OUT,d['page']))
                L['edizione']={'id':oid+'.e','deriva_da':oid+'.t','relazione':'edizione di','descrizione':'pagina di lettura nel browser, con il file originale scaricabile',
                    'versione':ver,'url':BASE+d['page'],'file':d['page'],'sha256':esha,'byte':eby}
            else:
                L['edizione']={'id':oid+'.e','deriva_da':oid+'.c','relazione':'pubblicazione di','descrizione':'file originale scaricabile, senza pagina di lettura (testo non estraibile)',
                    'versione':ver,'url':BASE+d['out'],'file':d['out'],'sha256':fsha,'byte':fby}
        else:
            L['cattura']={'id':oid+'.c','deriva_da':oid+'.o','relazione':'copia di',
                'descrizione':'nessuna copia del file: la Wayback Machine ha salvato solo la pagina che lo collegava',
                'wayback_timestamp':'','wayback_url':'','file':'','sha256':'','byte':''}
        tit=(d.get('title') or d.get('filename') or '').replace(' hot!','')
        oggetti.append({'id':oid,'tipo':'documento','titolo':tit,'stato':stato,'livelli':L,'interventi':I})
        c=L.get('cattura',{}); t=L.get('testo',{}); e=L.get('edizione',{})
        righe.append({'id':oid,'tipo':'documento','titolo':tit,'stato':stato,
            'originale_url':L['originale']['url'],'originale_data':L['originale']['data_pubblicazione'],
            'cattura_timestamp':c.get('wayback_timestamp',''),'cattura_url':c.get('wayback_url',''),'cattura_file':c.get('file',''),'cattura_sha256':c.get('sha256',''),
            'testo_metodo':t.get('metodo',''),'testo_sha256':t.get('sha256_testo_semplice',''),'testo_parole':t.get('parole',''),
            'edizione_file':e.get('file',''),'edizione_sha256':e.get('sha256',''),'edizione_versione':e.get('versione',''),'interventi':len(I)})
    od=os.path.join(OUT,'dati')
    meta={'titolo':'Provenienza dei testi dell’archivio, livello per livello','versione':ver,'generato':oggi,'modello':'dati/MODELLO.md',
          'livelli':{'o':'originale: la pubblicazione sul sito di Moscato','c':'cattura: la copia della Wayback Machine da cui proviene il testo',
                     't':'testo: il testo estratto o convertito','e':'edizione: la pagina di questo archivio',
                     'i':'interventi: eventi che hanno modificato qualcosa fra un livello e l’altro'},
          'nota':'Le impronte delle edizioni valgono per la versione indicata: ogni nuova versione le ricalcola. L’impronta del testo semplice permette di verificare che il testo non sia cambiato anche quando cambia l’impaginazione.'}
    json.dump({'meta':meta,'oggetti':oggetti},open(os.path.join(od,'provenienza.json'),'w'),ensure_ascii=False,indent=1)
    for name,rows in (('provenienza.csv',righe),('eventi.csv',eventi)):
        with open(os.path.join(od,name),'w',newline='',encoding='utf-8-sig') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    from collections import Counter
    return len(oggetti),len(eventi),Counter(e['tipo'] for e in eventi).most_common()
