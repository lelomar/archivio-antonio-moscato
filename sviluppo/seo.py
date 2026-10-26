# Post-elaborazione SEO / social: meta, Open Graph, JSON-LD, condivisione, sitemap, robots, llms.txt
import os,re,json,html,datetime,urllib.parse
BASE='https://lelomar.github.io/archivio-antonio-moscato/'
SITE='Movimento operaio – La pagina di Antonio Moscato'
DEFDESC='Archivio ricostruito del sito di Antonio Moscato (1938–2026), storico del movimento operaio: 2.928 articoli e 180 saggi dal 2009 al 2021, con ricerca a testo pieno. Consultabile anche offline.'
MOSCATO={"@type":"Person","@id":BASE+"#antonio-moscato","name":"Antonio Moscato","birthDate":"1938","birthPlace":"Roma","deathDate":"2026-10-24","jobTitle":"Storico del movimento operaio","affiliation":{"@type":"CollegeOrUniversity","name":"Università di Lecce"},"sameAs":["https://it.wikipedia.org/wiki/Antonio_Moscato","https://www.wikidata.org/wiki/Q3619928"]}
LL={"@type":"Person","@id":BASE+"#leonardo-lomartire","name":"Leonardo Lomartire","url":"https://lelomar.substack.com"}
def clean(t,n=158):
    t=html.unescape(re.sub(r'<[^>]+>',' ',t)); t=re.sub(r'\s+',' ',t).strip()
    return (t[:n].rsplit(' ',1)[0]+'…') if len(t)>n else t
def share(url,title):
    u=urllib.parse.quote(url,safe=''); t=urllib.parse.quote(title+' – '+url,safe=''); tt=urllib.parse.quote(title,safe='')
    L=[('WhatsApp',f'https://wa.me/?text={t}'),('Facebook',f'https://www.facebook.com/sharer/sharer.php?u={u}'),('X',f'https://x.com/intent/post?text={tt}&url={u}'),
       ('LinkedIn',f'https://www.linkedin.com/sharing/share-offsite/?url={u}'),('Telegram',f'https://t.me/share/url?url={u}&text={tt}'),('Email',f'mailto:?subject={tt}&body={u}')]
    return '<div class="share"><span>Condividi</span>'+''.join(f'<a href="{h}" target="_blank" rel="noopener">{n}</a>' for n,h in L)+f'<button type="button" data-copy="{html.escape(url)}">Copia link</button></div>'
def run(OUT,arts_info,today=None):
    today=today or datetime.date.today().isoformat(); urls=[]
    for dp,dn,fn in os.walk(OUT):
        dn[:]=[d for d in dn if d not in ('sviluppo','.git')]
        for f in fn:
            if not f.endswith('.html'): continue
            p=os.path.join(dp,f); rel=os.path.relpath(p,OUT).replace(os.sep,'/')
            s=open(p,encoding='utf-8').read()
            if 'name="robots" content="noindex"' in s: continue
            if 'property="og:title"' in s: s=re.sub(r'\n?<!--seo-->.*?<!--/seo-->','',s,flags=re.S); s=re.sub(r'<div class="share">.*?</div>','',s,flags=re.S)
            url=BASE+('' if rel=='index.html' else rel); urls.append((url,rel))
            pre='../'*rel.count('/')
            m=re.search(r'<title>(.*?)</title>',s,re.S); full=html.unescape(m.group(1)) if m else SITE
            short=full.split(' · ')[0]
            m=re.search(r'<p class="lead">(.*?)</p>',s,re.S) or re.search(r'<div class="lead">(.*?)</div>',s,re.S)
            desc=clean(m.group(1)) if m and clean(m.group(1)) else ''
            if not desc:
                m=re.search(r'id="testo">(.*?)</div>\s*<p class="orig"',s,re.S) or re.search(r'id="testo">(.{0,4000})',s,re.S)
                if m: desc=clean(m.group(1))
            if rel=='index.html': desc=DEFDESC; short=SITE
            mm=re.search(r'<p class="meta">(\d+) testi',s)
            if rel.startswith('temi/') and mm: desc=f"{short}: {mm.group(1)} testi sul tema nell’archivio di Antonio Moscato, storico del movimento operaio (2009–2021). Articoli, polemiche e saggi, con ricerca a testo pieno."
            if rel.startswith('anni/') and mm: desc=f"Tutti i {mm.group(1)} testi pubblicati nel {short} sul sito di Antonio Moscato, storico del movimento operaio, mese per mese."
            if rel=='progetto.html':
                short='Sono rimasto seduto. L’archivio ritrovato di Antonio Moscato'
                desc='Antonio Moscato (1938–2026), storico del movimento operaio, è stato il mio professore. Alla sua morte il suo sito era sparito: l’ho ricostruito. 2.928 articoli e 180 saggi, liberi e consultabili anche offline.' 
            if not desc or len(desc)<40: desc=f'{short}. {DEFDESC}'[:300]
            img=BASE+'assets/'+('og-progetto.png' if rel=='progetto.html' else 'og-archivio.png')
            otype='article' if rel.startswith(('articoli/','documenti/testo/')) or rel=='progetto.html' else 'website'
            ld=[]
            if rel=='index.html':
                ld=[{"@context":"https://schema.org","@type":"WebSite","@id":BASE+"#site","name":SITE,"alternateName":"Archivio Antonio Moscato","url":BASE,"inLanguage":"it","description":DEFDESC,"about":MOSCATO,"creator":LL,"license":"https://creativecommons.org/licenses/by-nc-sa/4.0/","identifier":"https://doi.org/10.5281/zenodo.23670900","sameAs":["https://doi.org/10.5281/zenodo.23670900","https://www.wikidata.org/wiki/Q141880166","https://archive.org/details/archivio-antonio-moscato","https://github.com/lelomar/archivio-antonio-moscato"],"potentialAction":{"@type":"SearchAction","target":{"@type":"EntryPoint","urlTemplate":BASE+"cerca.html?q={search_term_string}"},"query-input":"required name=search_term_string"}}]
            elif rel=='progetto.html':
                ld=[{"@context":"https://schema.org","@type":"Article","headline":short,"description":desc,"url":url,"image":img,"inLanguage":"it","datePublished":"2026-10-26","author":LL,"about":MOSCATO,"isPartOf":{"@id":BASE+"#site"}}]
            elif rel.startswith('articoli/'):
                aid=rel.split('/')[1][:-5]; ai=arts_info.get(aid,{})
                o={"@context":"https://schema.org","@type":"Article","headline":short[:110],"description":desc,"url":url,"image":img,"inLanguage":ai.get('lang','it'),"isPartOf":{"@type":"WebSite","@id":BASE+"#site","name":SITE,"url":BASE},"mentions":[]}
                if ai.get('date'): o["datePublished"]=ai['date']
                if ai.get('kws'): o["keywords"]=', '.join(ai['kws'])
                if ai.get('cat'): o["articleSection"]=ai['cat']
                o.pop('mentions'); ld=[o]
            elif rel.startswith('documenti/testo/'):
                ld=[{"@context":"https://schema.org","@type":"CreativeWork","name":short,"description":desc,"url":url,"inLanguage":"it","isPartOf":{"@id":BASE+"#site"}}]
            else:
                ld=[{"@context":"https://schema.org","@type":"CollectionPage","name":short,"description":desc,"url":url,"inLanguage":"it","isPartOf":{"@id":BASE+"#site"}}]
            E=lambda x:html.escape(x,quote=True)
            head=f'''<!--seo--><meta name="description" content="{E(desc)}"><link rel="canonical" href="{url}"><meta name="robots" content="index,follow,max-image-preview:large">
<meta name="author" content="{'Leonardo Lomartire' if rel=='progetto.html' else 'Antonio Moscato'}"><meta name="theme-color" content="#a3201b">
<link rel="icon" href="{pre}assets/favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="{pre}assets/apple-touch-icon.png">
<meta property="og:site_name" content="{E(SITE)}"><meta property="og:locale" content="it_IT"><meta property="og:type" content="{otype}">
<meta property="og:title" content="{E(short)}"><meta property="og:description" content="{E(desc)}"><meta property="og:url" content="{url}">
<meta property="og:image" content="{img}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="{E(short)} – archivio di Antonio Moscato">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{E(short)}"><meta name="twitter:description" content="{E(desc)}"><meta name="twitter:image" content="{img}">
<script type="application/ld+json">{json.dumps(ld[0] if len(ld)==1 else ld,ensure_ascii=False)}</script><!--/seo-->'''
            s=s.replace('</title>','</title>\n'+head,1)
            if rel.startswith('articoli/') or rel=='progetto.html' or rel.startswith('documenti/testo/'):
                s=s.replace('</article>',share(url,short)+'</article>',1)
            elif rel=='index.html':
                s=s.replace('<p class="quick">',share(url,SITE)+'<p class="quick">',1)
            open(p,'w',encoding='utf-8').write(s)
    pri=lambda r:'1.0' if r in('index.html','progetto.html') else '0.8' if r.endswith('.html') and '/' not in r else '0.6'
    with open(os.path.join(OUT,'sitemap.xml'),'w') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for u,r in sorted(urls,key=lambda x:(x[1]!='index.html',x[1]!='progetto.html',x[1])):
            f.write(f'<url><loc>{html.escape(u)}</loc><lastmod>{today}</lastmod><priority>{pri(r)}</priority></url>\n')
        f.write('</urlset>\n')
    open(os.path.join(OUT,'robots.txt'),'w').write(f'User-agent: *\nAllow: /\n\nSitemap: {BASE}sitemap.xml\n')
    open(os.path.join(OUT,'llms.txt'),'w').write(f'''# {SITE}

> Archivio ricostruito del sito di Antonio Moscato (Roma 1938 – 2026), storico del movimento operaio e militante della Quarta Internazionale, docente di Storia del movimento operaio all'università di Lecce. Il sito originale, antoniomoscato.altervista.org (2009–2021), è stato ricostruito nell'ottobre 2026 da Leonardo Lomartire, suo ex studente, a partire dalle copie dell'Internet Archive.

Contiene 2.928 articoli (2009–2021) su movimento operaio, "socialismo reale" e stalinismo, Cuba e Che Guevara, America Latina, Medio Oriente, sinistra italiana e sindacato, e 180 saggi e documenti storici ("I grandi nodi del Novecento"). Lingue: italiano e spagnolo.

## Pagine principali
- [Il progetto: chi era Antonio Moscato e come è stato ricostruito l'archivio]({BASE}progetto.html)
- [Chi è Antonio Moscato (biografia e bibliografia scritte da lui)]({BASE}articoli/22.html)
- [Le rubriche]({BASE}attualita.html)
- [I grandi nodi del Novecento: saggi e documenti]({BASE}documenti/index.html)
- [Indice dei temi]({BASE}temi.html)
- [Cronologia per anno]({BASE}anni.html)
- [Ricerca]({BASE}cerca.html)
- [DOI permanente (Zenodo)](https://doi.org/10.5281/zenodo.23670900)
- [Copia completa scaricabile su Internet Archive](https://archive.org/details/archivio-antonio-moscato)
- [Scheda Wikidata dell’archivio (Q141880166)](https://www.wikidata.org/wiki/Q141880166)

## Citazione
Per citare l'archivio nel suo insieme: Lomartire, L. (2026). Movimento operaio – La pagina di Antonio Moscato. Archivio ricostruito (2009-2021). Zenodo. https://doi.org/10.5281/zenodo.23670900. Quando citi questi materiali indica l'autore del testo, il titolo, "Movimento operaio – La pagina di Antonio Moscato", archivio ricostruito da Leonardo Lomartire, e l'URL della pagina.

## Licenze
Testi: diritti dei rispettivi autori ed eredi. Lavoro di cura: CC BY-NC-SA 4.0. Codice: GPL-3.0. Sorgenti: https://github.com/lelomar/archivio-antonio-moscato
''')
    return len(urls)
