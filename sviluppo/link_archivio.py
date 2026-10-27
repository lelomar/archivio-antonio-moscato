# Riscrive i link esterni degli articoli verso la copia della Wayback Machine
# salvata nei giorni in cui Moscato li citava (dati da cerca_link_wayback.py),
# conservando l'indirizzo originale. Scrive anche dati/link-esterni.csv/.json.
import os,re,json,glob,html,csv,urllib.parse
MESI=['gennaio','febbraio','marzo','aprile','maggio','giugno','luglio','agosto','settembre','ottobre','novembre','dicembre']
def _data(ts):
    g=int(ts[6:8]); return ('dell’' if g in (1,8,11) else 'del ')+f'{g} {MESI[int(ts[4:6])-1]} {ts[:4]}'
def run(OUT,WORK):
    wb=json.load(open(os.path.join(WORK,'link_wayback.json')))
    ext=json.load(open(os.path.join(WORK,'link_esterni.json')))
    A=re.compile(r'<a\s([^>]*?)href="(https?://[^"]+)"([^>]*)>(.*?)</a>',re.S)
    tot={'archiviato':0,'non archiviato':0}
    def sub(m):
        pre,href,post,txt=m.groups()
        u=html.unescape(href).strip(); h=urllib.parse.urlsplit(u).netloc.lower()
        if 'archive.org' in h or 'antoniomoscato' in h: return m.group(0)
        r=wb.get(u)
        if not r or r.get('stato')=='errore': return m.group(0)
        attrs=re.sub(r'\s*(target|rel|title|class)="[^"]*"','',pre+post).strip()
        attrs=(' '+attrs) if attrs else ''
        ue=html.escape(u,quote=True)
        if r['stato']=='archiviato':
            tot['archiviato']+=1
            ts=r['timestamp']; d=_data(ts)
            return (f'<a{attrs} class="lx" href="https://web.archive.org/web/{ts}/{ue}" target="_blank" rel="noopener" '
                    f'title="Copia d’archivio {d} · indirizzo originale: {ue}">{txt}</a>'
                    f'<a class="lx-o" href="{ue}" target="_blank" rel="noopener nofollow" title="Indirizzo originale, oggi forse non più attivo" aria-label="indirizzo originale">orig.</a>')
        tot['non archiviato']+=1
        return (f'<a{attrs} class="lx-na" href="{ue}" target="_blank" rel="noopener nofollow" '
                f'title="Nessuna copia d’archivio: il link potrebbe non funzionare più">{txt}</a>'
                f'<span class="lx-n" title="La Wayback Machine non ha conservato questa pagina">non archiviato</span>')
    n=0
    for f in glob.glob(os.path.join(OUT,'articoli','*.html')):
        s=open(f,encoding='utf-8').read()
        m=re.search(r'(<div class="testo"[^>]*>)(.*?)(</div>\s*(?:<section class="scheda"|<div class="segnala"|<p class="orig"))',s,re.S)
        if not m: continue
        b=A.sub(sub,m.group(2))
        if b!=m.group(2):
            open(f,'w',encoding='utf-8').write(s[:m.start(2)]+b+s[m.end(2):]); n+=1
    # dati
    os.makedirs(os.path.join(OUT,'dati'),exist_ok=True)
    righe=[]
    for u,e in sorted(ext.items()):
        r=wb.get(u,{}); st=r.get('stato','non verificato')
        if st=='errore': st='non verificato'
        ts=r.get('timestamp','')
        righe.append({'url_originale':u,'stato':st,'copia_wayback':f'https://web.archive.org/web/{ts}/{u}' if ts else '',
            'data_copia':f'{ts[:4]}-{ts[4:6]}-{ts[6:8]}' if ts else '','giorni_dalla_citazione':r.get('giorni_dalla_citazione',''),
            'prima_citazione':e.get('data',''),'articoli':' '.join(str(x) for x in e['articoli'])})
    with open(os.path.join(OUT,'dati','link-esterni.csv'),'w',newline='',encoding='utf-8') as fh:
        w=csv.DictWriter(fh,fieldnames=list(righe[0])); w.writeheader(); w.writerows(righe)
    json.dump(righe,open(os.path.join(OUT,'dati','link-esterni.json'),'w'),ensure_ascii=False,indent=1)
    return {'pagine':n,**tot,'righe':len(righe)}
