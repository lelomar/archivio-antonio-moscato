import json,re,collections,sys
T=json.load(open(sys.argv[1]))
prev={r['id']:r for r in json.load(open('autori_proposte.json'))}
NONP=set('Venezuela Grecia Brasile Cuba Spagna Portogallo Ecuador Francia Siria Catalogna Germania Israele Nicaragua Argentina Ucraina Libia Bolivia Egitto Sudafrica Turchia Gaza Scuola PORTOGALLO Austria Angola USA Honduras America Cile Messico Perù Uruguay Colombia Iran Iraq Russia Cina Palestina Tunisia Marocco Algeria Polonia Ungheria Irlanda Islanda Belgio Olanda Svezia Danimarca Norvegia Finlandia Romania Bulgaria Serbia Kosovo Bosnia Croazia Slovenia Albania Macedonia Cipro Malta Libano Giordania Yemen Afghanistan Pakistan India Kurdistan Rojava Haiti Paraguay Guatemala Salvador Panama Europa Italia Fiat Fiom Cgil Pd Prc Napolitano Renzi Berlusconi Grillo Obama Trump Putin Chávez Maduro Lula Dilma Tsipras Syriza Podemos Erdogan Assad Netanyahu Fidel Raúl Castro Guevara Che Mélenchon Hollande Macron Merkel Monti Letta Bersani Vendola Landini Camusso Marchionne Bergoglio Papa Francesco Ratzinger Stalin Lenin Trotskij Trotsky Marx Gramsci Togliatti Berlinguer Mao Corbyn Sanders Morales Correa Kirchner Macri Bolsonaro Temer Ortega'.split())
U=r"[A-ZÀ-ÝŁŠŽČÉ]"; L=r"[a-zà-ÿ'’\-]"
TOK=rf"{U}{L}+(?:-{U}{L}+)?\.?"
NAMEP=rf"{TOK}(?:\s+(?:de|del|dos|das|van|von|la)?\s*{TOK}){{1,3}}"
SP=re.compile(rf"^(?:(?:di|Di|DI|Por|por|By|by|de|De)\s+)?({NAMEP})\s*\*?\s*(?:\([^)]{{0,80}}\))?\s*(?:[,–\-|]\s*.{{0,70}}|\s+da\s+.{{0,60}}|\s+\(?(?:www\.|https?://)\S+\)?)?$")
CAPS=re.compile(r"^([A-ZÀ-ÝÉ]{2,}(?:\s+[A-ZÀ-ÝÉ]{2,}){1,3})\s*\*?$")
AM=re.compile(r"\(\s*a\.\s?m\.?[^)]{0,30}\)|\[\s*a\.\s?m\.[^\]]{0,30}\]|\ba\.\s?m\.(?=[\s),;\]]|$)|\bA\.\s?M\.(?=[\s),;\]]|$)|\(am\)")
BYL=re.compile(rf"^\W{{0,3}}(?:di|Di|DI|[Pp]or|[Bb]y)\s+({NAMEP})")
PUB=re.compile(rf"(?i:articolo|testo|intervento|contributo|lettera|analisi|riflession\w+|nota|saggio|pezzo|commento|scritto|intervista|editoriale|appello|documento)\b[^.]{{0,60}}?\b(?i:di|del|della|dello|a cura di|scritt[oa] da|firmat[oa] da|a|con)\s+({NAMEP})")
STOPW=set('Tags Note Nota Posted Pubblicato Leggi Fonte Traduzione Premessa Postilla Introduzione Comunicato Appello Dossier Intervista Allegato Gennaio Febbraio Marzo Aprile Maggio Giugno Luglio Agosto Settembre Ottobre Novembre Dicembre Lunedì Martedì Mercoledì Giovedì Venerdì Sabato Domenica Il La Lo Le Gli Un Una Per Con Dal Dalla Nel Nella Del Della Sul Sulla Ma Non Che Questo Questa Ecco Cari Caro Care Compagni Compagne Viva Abbasso Ciao Grazie Partito Governo Stato Movimento Sindacato Consiglio Comitato Coordinamento Associazione Sinistra Lega Fronte Unione Rete Collettivo Redazione Ufficio Sciopero Lettera Manifesto Repubblica Corriere Stampa Dichiarazione Programma Notizie Breve Ultime Prima Seconda Parte Capitolo Antonio'.split())
def okname(n):
    toks=n.split()
    if any(t.rstrip('.') in NONP or t in STOPW for t in toks): return False
    if len(n)>45: return False
    return True
def trim(n,after):
    toks=n.split()
    while len(toks)>2 and re.match(r"^\s+[a-zà-ÿ]",after):
        after=' '+toks.pop()+after
    return ' '.join(toks)
def norm(n):
    n=re.sub(r"\s+da\s+.*$","",n).strip().rstrip('.')
    t=n.split()
    if len(t)==4 and t[:2]==t[2:]: n=' '.join(t[:2])
    n=re.sub(r"\s*\*$","",n).strip()
    if n.isupper(): n=' '.join(w.capitalize() for w in n.split())
    return n
KN=set()
for r in prev.values():
    if r['autore'] and r['autore']!='Antonio Moscato' and r['certezza']=='alta' and ' e ' not in r['autore']: KN.add(r['autore'])
SUR={n.split()[-1]:n for n in KN}
res=[]
for t in T:
    f=t['full']; ps=[p[0] for p in t['ps'] if p[0]!='…']; ti=t['t']
    # escludi coda "Tags:"
    body=re.split(r"\sTags:\s",f)[0]; W=len(body.split())
    ams=[m for m in AM.finditer(body)]
    am_intro=None; am_end=False
    for m in ams:
        after=len(body[m.end():].split())
        if after<=120: am_end=True
        elif m.start()<len(body)*0.5 and after>150 and am_intro is None: am_intro=m
    mosc_sig=am_end or bool(re.search(r"(?:^|\s)(?:di|Di)\s+Antonio Moscato",body[:200])) or bool(re.search(r"Antonio Moscato\W{0,6}$",body))
    seg=body[am_intro.end():] if am_intro else body
    intro=body[:am_intro.start()] if am_intro else body[:600]
    # paragrafi del segmento
    if am_intro:
        k=0
        for i,p in enumerate(ps):
            if AM.search(p): k=i+1; break
        segps=ps[k:k+8]
    else: segps=ps[:8]
    a=None;cert=None;how=''
    m=BYL.search(seg[:300])
    if m: m=type('M',(),{'g':trim(m.group(1),seg[m.end():m.end()+20])})(); m.group=lambda i,_m=m:_m.g
    if m and okname(m.group(1)) and not m.group(1).startswith('Antonio Moscato'): a=m.group(1);cert='alta';how='firma «di …» in apertura'
    if not a:
        for p in segps:
            mb=BYL.match(p)
            if mb and okname(trim(mb.group(1),p[mb.end():mb.end()+20])) and not mb.group(1).startswith('Antonio Moscato'):
                a=trim(mb.group(1),p[mb.end():mb.end()+20]);cert='alta';how='firma «di …»: «'+p[:80]+'»';break
    if not a:
        for p in segps:
            m=SP.match(p) or None
            if m and okname(m.group(1)) and not re.search(r'\d{3,}|tel\.|fax',p): a=m.group(1);cert='alta';how='nome isolato all’inizio del testo: «'+p[:80]+'»';break
            m2=CAPS.match(p)
            if m2:
                nn=norm(m2.group(1))
                if nn in KN or (nn.split()[-1] in SUR and len(nn.split())>=2): a=nn;cert='alta';how='nome in maiuscolo: «'+p+'»';break
    if not a:
        m=re.search(rf"({NAMEP})\s*\*",seg[:400])
        if m and okname(m.group(1)): a=m.group(1);cert='alta';how='nome con asterisco: «'+seg[max(0,m.start()-20):m.end()+30]+'»'
    if not a:
        m=PUB.search(intro)
        if m and okname(m.group(1)) and not m.group(1).startswith('Antonio Moscato'): a=trim(m.group(1),intro[m.end():m.end()+20]);cert='alta' if a in KN else 'media';how='presentazione: «'+intro[max(0,m.start()-50):m.end()+10]+'»'
    if not a:
        mt=re.match(rf"^({TOK}(?:\s+{TOK})?)\s*[:|]\s+",ti)
        if mt:
            w=mt.group(1); last=w.split()[-1]
            if last in SUR: a=SUR[last];cert='alta';how='cognome nel titolo'
            elif len(w.split())==2 and okname(w): a=w;cert='media';how='nome nel titolo'
    if not a:
        for p in ps[-3:]:
            m=SP.match(p)
            if m and okname(m.group(1)) and not m.group(1).startswith('Antonio Moscato'): a=m.group(1);cert='media';how='firma in fondo: «'+p[:80]+'»';break
    if not a:
        for n in sorted(KN,key=len,reverse=True):
            i=seg[:300].find(n)
            if i>=0: a=n;cert='media';how='nome noto all’inizio: «'+seg[max(0,i-40):i+len(n)+30]+'»';break
    if a:
        a=norm(a); a=SUR.get(a.split()[-1],a) if a.split()[-1] in SUR and len(a.split())==1 else a
        res.append(dict(id=t['id'],titolo=ti,data=t['d'],lingua=t['lang'],autore=a,moscato='introduzione di Antonio Moscato' if (am_intro or (ams and not am_end)) else ('postilla di Antonio Moscato' if am_end else ''),certezza=cert,indizio=how[:220]))
    elif ams or mosc_sig:
        res.append(dict(id=t['id'],titolo=ti,data=t['d'],lingua=t['lang'],autore='Antonio Moscato',moscato='',certezza='alta',indizio='sigla a.m. o firma Antonio Moscato'))
    else:
        res.append(dict(id=t['id'],titolo=ti,data=t['d'],lingua=t['lang'],autore='Antonio Moscato' if t['lang']!='es' else '',moscato='',certezza='presunta' if t['lang']!='es' else 'bassa',indizio='nessuna firma trovata'))
json.dump(res,open('autori_proposte2.json','w'),ensure_ascii=False,indent=0)
c=collections.Counter((r['certezza'],r['autore']=='Antonio Moscato') for r in res); print(c)
print(collections.Counter(r['moscato'] for r in res))
