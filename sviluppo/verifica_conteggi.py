# Controlla che i testi descrittivi (README, wiki, metadati, script GitHub, pagine) riportino i numeri
# calcolati a ogni costruzione in dati/conteggi.json. Segnala le cifre che non corrispondono.
# Uso: python3 sviluppo/verifica_conteggi.py SITO_MOSCATO [cartella antoniomoscato]
import os,re,sys,json,glob
OUT=sys.argv[1]; ROOT=sys.argv[2] if len(sys.argv)>2 else os.path.dirname(os.path.abspath(OUT))
C=json.load(open(os.path.join(OUT,'dati','conteggi.json')))
def n(x): return int(x.replace('.',''))
# cifre ammesse per ogni grandezza: il valore corrente e, dove il testo racconta i passaggi, quelli intermedi
AMM={
 'articoli':{C['articoli'],C['articoli_prima_della_pulizia'],C['articoli_joomla_estratti'],C['articoli_joomla_estratti']-1},
 'documenti_tot':{C['documenti']},
 'documenti_in':{C['documenti_in_archivio']},
 'incompleti':{C['documenti_incompleti']},
 'mancanti':{C['documenti_mancanti']},
 'temi':{C.get('temi_con_pagina'),C.get('temi_nel_vocabolario'),C.get('temi_con_wikidata')},
}
REGOLE=[
 (r'(\d[\d.]*)\s+articoli','articoli'),
 (r'(\d[\d.]*)\s+(?:dei|su)\s+247\b','documenti_in'),
 (r'(\d+)\s+(?:dei|su)\s+(\d+)\s+(?:documenti|saggi)','documenti_tot',2),
 (r'(\d+)\s+(?:documenti\s+)?incomplet','incompleti'),
 (r'(\d+)\s+documenti\s+(?:mancanti|mai salvati)','mancanti'),
 (r'(\d[\d.]*\d|\d)\s+temi\b','temi'),
]
FILE=[os.path.join(OUT,'README.md'),os.path.join(OUT,'CITATION.cff'),os.path.join(OUT,'.zenodo.json'),os.path.join(OUT,'dati','LEGGIMI.md'),
      os.path.join(OUT,'index.html'),os.path.join(OUT,'progetto.html'),os.path.join(OUT,'documenti','index.html')]
FILE+=glob.glob(os.path.join(ROOT,'wiki','*.md'))+glob.glob(os.path.join(ROOT,'github','*.sh'))+glob.glob(os.path.join(ROOT,'github','discussioni','*.md'))
prob=[]
for f in FILE:
    if not os.path.exists(f): continue
    s=re.sub(r'<[^>]+>',' ',open(f,encoding='utf-8',errors='ignore').read())
    for r in REGOLE:
        rx,k=r[0],r[1]; g=r[2] if len(r)>2 else 1
        for m in re.finditer(rx,s,re.I):
            v=n(m.group(g))
            if k=='articoli' and v<1000: continue  # 110 in spagnolo, 335 con note… sono sottoinsiemi
            amm=', '.join(str(x) for x in sorted(x for x in AMM[k] if x))
            if v not in AMM[k]: prob.append(f'{os.path.relpath(f,ROOT)}: «{m.group(0)}» (ammessi: {amm})')
if prob:
    print('conteggi da controllare:'); [print('  '+p) for p in prob]
else:
    print('conteggi coerenti in',len([f for f in FILE if os.path.exists(f)]),'file')
