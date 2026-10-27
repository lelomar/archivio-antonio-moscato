# Vocabolario dei temi a due livelli.
#  1. Le parole chiave originali, esattamente come Moscato (o chi pubblicava) le scriveva per ogni articolo:
#     non vengono mai modificate né cancellate (dati/parole-chiave-originali.csv).
#  2. Le entità normalizzate a cui ogni parola chiave è ricondotta, con un tipo (persona, organizzazione,
#     luogo, evento, concetto, pubblicazione) e, dove esistono, identificativi esterni (Wikidata, VIAF, SBN, GeoNames).
# Scrive dati/vocabolario-temi.csv/.json, dati/parole-chiave-originali.csv, dati/vocabolario-da-verificare.csv,
# dati/vocabolario-temi.skos.ttl.
import os,csv,json,collections,datetime
BASE='https://lelomar.github.io/archivio-antonio-moscato/'
TIPI=['persona','organizzazione','luogo','evento','concetto','pubblicazione']
ETI={'persona':'Persona','organizzazione':'Organizzazione','luogo':'Luogo','evento':'Evento storico','concetto':'Concetto','pubblicazione':'Pubblicazione','non classificato':'Non ancora classificato'}
def classifica(TC,kwcount,lab2key,risolvi):
    """Restituisce {chiave: (tipo, stato)} per ogni entità del vocabolario."""
    T={}
    for tipo,labs in TC.get('tipi',{}).items():
        for l in labs:
            for k in risolvi(lab2key(l)): T.setdefault(k,tipo)
    AMB={}
    for l,motivo in TC.get('ambigue',{}).items():
        for k in risolvi(lab2key(l)): AMB[k]=motivo
    out={}
    for k,n in kwcount.items():
        if k in T: out[k]=(T[k],'ambigua' if k in AMB else 'curata')
        elif n>=2: out[k]=('concetto','ambigua' if k in AMB else 'curata')
        else: out[k]=('non classificato','da classificare')
    return out,AMB
def run(OUT,WORK,kwcount,KWSLUG,kwname,ORIGKW,TIPO,AMB,wd,IDENT,arts_by_id):
    od=os.path.join(OUT,'dati'); os.makedirs(od,exist_ok=True)
    forme=collections.defaultdict(collections.Counter)
    for aid,pos,forma,tratt,chiavi in ORIGKW:
        for k in chiavi: forme[k][forma]+=1
    voc=[]
    for k in sorted(kwcount,key=lambda k:(-kwcount[k],kwname(k))):
        w=wd(k) or {}; idt=IDENT.get(w.get('id',''),{})
        tipo,stato=TIPO.get(k,('non classificato','da classificare'))
        voc.append({'id':KWSLUG[k],'etichetta':kwname(k),'tipo':tipo,'classificazione':stato,'nota':AMB.get(k,''),
            'testi':kwcount[k],'forme_originali':'; '.join(f'{f} ({n})' for f,n in forme[k].most_common()),
            'wikidata':w.get('id',''),'wikidata_descrizione':w.get('desc',''),'viaf':idt.get('viaf',''),'sbn':idt.get('sbn',''),'geonames':idt.get('geonames',''),
            'pagina':BASE+'temi/'+KWSLUG[k]+'.html' if kwcount[k]>=3 else '','chiave':k})
    with open(os.path.join(od,'vocabolario-temi.csv'),'w',newline='',encoding='utf-8-sig') as f:
        w_=csv.DictWriter(f,fieldnames=list(voc[0].keys())); w_.writeheader(); w_.writerows(voc)
    cont=collections.Counter(v['tipo'] for v in voc)
    json.dump({'meta':{'titolo':'Vocabolario dei temi','versione_generata':datetime.date.today().isoformat(),'licenza':'CC BY-NC-SA 4.0',
        'descrizione':'Entità normalizzate ricavate dalle parole chiave originali degli articoli. Le parole chiave originali non sono modificate: sono in parole-chiave-originali.csv, con il trattamento ricevuto da ciascuna.',
        'tipi':{t:ETI[t] for t in TIPI+['non classificato']},'conteggio_per_tipo':dict(cont)},'temi':voc},
        open(os.path.join(od,'vocabolario-temi.json'),'w'),ensure_ascii=False,indent=1)
    # parole chiave originali, una riga per articolo e parola chiave
    with open(os.path.join(od,'parole-chiave-originali.csv'),'w',newline='',encoding='utf-8-sig') as f:
        w_=csv.writer(f); w_.writerow(['articolo','titolo','posizione','forma_originale','trattamento','temi','tipi'])
        for aid,pos,forma,tratt,chiavi in ORIGKW:
            a=arts_by_id.get(str(aid),{})
            w_.writerow([f'AM-{aid}',a.get('title',''),pos,forma,tratt,'; '.join(kwname(k) for k in chiavi),'; '.join(TIPO.get(k,('',''))[0] for k in chiavi)])
    # casi da verificare
    with open(os.path.join(od,'vocabolario-da-verificare.csv'),'w',newline='',encoding='utf-8-sig') as f:
        w_=csv.writer(f); w_.writerow(['tema','testi','motivo','pagina'])
        for v in voc:
            if v['classificazione']=='ambigua': w_.writerow([v['etichetta'],v['testi'],v['nota'],v['pagina']])
    # SKOS
    def lit(s): return '"'+s.replace('\\','\\\\').replace('"','\\"')+'"'
    T=['@prefix skos: <http://www.w3.org/2004/02/skos/core#> .','@prefix dct: <http://purl.org/dc/terms/> .','@prefix wd: <http://www.wikidata.org/entity/> .',
       f'@prefix am: <{BASE}temi/> .',f'@prefix tipo: <{BASE}dati/vocabolario-temi#tipo-> .','',
       f'<{BASE}dati/vocabolario-temi> a skos:ConceptScheme ; skos:prefLabel "Vocabolario dei temi dell’archivio di Antonio Moscato"@it ; dct:license <https://creativecommons.org/licenses/by-nc-sa/4.0/> .','']
    for t in TIPI:
        T.append(f'tipo:{t} a skos:Concept ; skos:prefLabel {lit(ETI[t])}@it ; skos:topConceptOf <{BASE}dati/vocabolario-temi> .')
    T.append('')
    for v in voc:
        p=[f'am:{v["id"]} a skos:Concept',f'skos:inScheme <{BASE}dati/vocabolario-temi>',f'skos:prefLabel {lit(v["etichetta"])}@it']
        for fo in forme[v['chiave']]:
            if fo!=v['etichetta']: p.append(f'skos:altLabel {lit(fo)}')
        if v['tipo'] in TIPI: p.append(f'skos:broader tipo:{v["tipo"]}')
        if v['wikidata']: p.append(f'skos:exactMatch wd:{v["wikidata"]}')
        if v['viaf']: p.append(f'skos:exactMatch <http://viaf.org/viaf/{v["viaf"]}>')
        if v['geonames']: p.append(f'skos:exactMatch <https://sws.geonames.org/{v["geonames"]}/>')
        if v['nota']: p.append(f'skos:editorialNote {lit("da verificare: "+v["nota"])}@it')
        T.append(' ;\n  '.join(p)+' .')
    open(os.path.join(od,'vocabolario-temi.skos.ttl'),'w').write('\n'.join(T)+'\n')
    tratt=collections.Counter(x[3] for x in ORIGKW)
    return {'entita':len(voc),'per_tipo':dict(cont),'parole_chiave_originali':len(ORIGKW),'trattamento':dict(tratt),'da_verificare':sum(1 for v in voc if v['classificazione']=='ambigua')}
