# Archivio Antonio Moscato – prima versione di Leonardo Lomartire (2026) – GPL-3.0 con attribuzione, vedi LICENZA.md
import os,re,json,sys,urllib.parse,html,unicodedata,collections
from bs4 import BeautifulSoup
WORK=os.environ.get('MOSCATO_WORK',os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else '.')
root=sys.argv[1]; out=sys.argv[2]
M=json.load(open(os.path.join(WORK,'map.json')))
MESI={m:i+1 for i,m in enumerate(['gennaio','febbraio','marzo','aprile','maggio','giugno','luglio','agosto','settembre','ottobre','novembre','dicembre'])}
def qs(u): return urllib.parse.parse_qs(urllib.parse.urlparse(html.unescape(u)).query)
def num(x):
    m=re.match(r'\s*(\d+)',x or ''); return int(m.group(1)) if m else None
def slugpart(x):
    return x.split(':',1)[1] if x and ':' in x else ''
def jdate(t):
    t=t.lower()
    m=re.search(r'(\d{1,2})\s+([a-zà-ù]+)\s+(\d{4})(?:\s+(\d{1,2}):(\d{2}))?',t)
    if m and m.group(2) in MESI:
        return '%s-%02d-%02d'%(m.group(3),MESI[m.group(2)],int(m.group(1)))
    return ''
def norm(t):
    t=unicodedata.normalize('NFKD',t.lower()); t=''.join(c for c in t if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]+','',t)
arts={}      # key -> dict
cats={}      # catid -> name
sections={}  # secid -> {name, cats:set}
docs={}      # gid -> {title,filename,desc,date,file}
pdfart={}    # article id -> pdf file
wp={}
def body_score(b): return len(b.get_text()) if b else 0
files=[]
for dp,dn,fn in os.walk(root):
    if '/_sito' in dp or '/SITO' in dp: continue
    for f in fn: files.append(os.path.relpath(os.path.join(dp,f),root))
for i,rel in enumerate(files):
    p=os.path.join(root,rel)
    urls=M.get(rel,[])
    try: raw=open(p,'rb').read()
    except: continue
    head=raw[:8]
    q=qs(urls[0]) if urls else {}
    # binary documents
    if head.startswith(b'%PDF') or head.startswith(b'{\\rtf') or head.startswith(b'PK') or head.startswith(b'\xd0\xcf\x11\xe0'):
        ext='pdf' if head.startswith(b'%PDF') else 'rtf' if head.startswith(b'{\\rtf') else 'doc' if head.startswith(b'\xd0') else 'zip'
        for u in urls:
            qq=qs(u)
            if 'doc_download' in qq.get('task',[]) or 'doc_view' in qq.get('task',[]):
                g=num(qq.get('gid',[''])[0])
                if g is not None:
                    d=docs.setdefault(g,{}); d.setdefault('file',rel); d['ext']=ext
            if qq.get('format')==['pdf']:
                a=num(qq.get('id',[''])[0])
                if a: pdfart[a]=rel
        if not urls or not any(('gid' in u or 'format=pdf' in u) for u in urls):
            # loose files like images/stories/*.pdf
            if rel.lower().endswith(('.pdf','.rtf','.doc')):
                docs.setdefault('f:'+rel,{'file':rel,'ext':ext,'title':os.path.basename(rel)})
        continue
    if b'<' not in raw[:2000]: continue
    s=raw.decode('utf-8','ignore')
    if 'contentheading' in s and 'article-content' in s:
        soup=BeautifulSoup(s,'lxml')
        for h in soup.select('.contentheading'):
            a=h.find('a'); href=a['href'] if a and a.has_attr('href') else (urls[0] if urls else '')
            qq=qs(href)
            if qq.get('view')!=['article'] and q.get('view')==['article']: qq=q
            aid=num(qq.get('id',[''])[0])
            if aid is None: continue
            # find container siblings
            cont=h.find_parent()
            b=cont.select_one('.article-content') if cont else None
            if not b: continue
            dt=cont.select_one('.createdate')
            title=h.get_text(' ',strip=True)
            cid=num(qq.get('catid',[''])[0])
            # only take full-article pages: url of this file is the article itself, or single article
            single = (q.get('view')==['article'] and num(q.get('id',[''])[0])==aid)
            readmore = cont.select_one('.readon, a.readon')
            rec=arts.get(aid)
            sc=body_score(b) + (100000 if single else 0) - (50000 if readmore and not single else 0)
            if rec and rec['score']>=sc: 
                if cid and not rec.get('catid'): rec['catid']=cid
                continue
            arts[aid]={'id':aid,'title':title,'date':jdate(dt.get_text()) if dt else '','catid':cid or (rec or {}).get('catid'),
                       'catslug':slugpart(qq.get('catid',[''])[0]),'slug':slugpart(qq.get('id',[''])[0]),
                       'html':str(b),'score':sc,'src':rel,'kw':''}
            mk=soup.find('meta',attrs={'name':'keywords'})
            if single and mk: arts[aid]['kw']=mk.get('content','')
    # category / section names
    if q.get('option')==['com_content'] and q.get('view') in (['category'],['section']) and '<' in s[:500]:
        soup=BeautifulSoup(s,'lxml')
        ch=soup.select_one('.componentheading') or soup.select_one('h1')
        idn=num(q.get('id',[''])[0])
        if idn and ch:
            nm=ch.get_text(' ',strip=True)
            if q['view']==['category']: cats.setdefault(idn,nm)
            else:
                sec=sections.setdefault(idn,{'name':nm,'cats':set()})
                for a in soup.find_all('a',href=True):
                    qa=qs(a['href'])
                    if qa.get('view')==['category']:
                        c=num(qa.get('id',[''])[0])
                        if c: sec['cats'].add(c); cats.setdefault(c,a.get_text(' ',strip=True))
    # menu: sections and categories from menu links (any page)
    if 'dm_details' in s:
        soup=BeautifulSoup(s,'lxml')
        dl=soup.select_one('.dm_taskbar a[href*="doc_download"]')
        if dl:
            g=num(qs(dl['href']).get('gid',[''])[0])
            rows={}
            for tr in soup.select('#dm_details tbody tr'):
                tds=tr.find_all('td')
                if len(tds)>=2: rows[tds[0].get_text(strip=True)]=tds[1].get_text(' ',strip=True)
            d=docs.setdefault(g,{})
            d['title']=rows.get('Nome',''); d['filename']=rows.get('Nome del file',''); d['desc']=rows.get('Descrizione','')
            d['date']=rows.get('Creato il:','')
    if 'entry-content' in s and 'entry-title' in s and '<article' in s:
        soup=BeautifulSoup(s,'lxml')
        arts_wp=soup.select('article')
        if len(arts_wp)==1:
            a=arts_wp[0]; t=a.select_one('.entry-title'); b=a.select_one('.entry-content')
            can=soup.find('link',rel='canonical')
            if t and b and can:
                slug=urllib.parse.urlparse(can['href']).path.strip('/')
                if slug and '/' not in slug:
                    tm=a.find('time')
                    cat=[x.get_text(strip=True) for x in a.select('a[rel~="category"]')]
                    rec=wp.get(slug)
                    if not rec or len(b.get_text())>rec['len']:
                        wp[slug]={'slug':slug,'title':t.get_text(' ',strip=True),'date':(tm.get('datetime','')[:10] if tm else ''),
                                  'cats':cat,'html':str(b),'len':len(b.get_text()),'src':rel}
    if i%1000==0: print(i,len(arts),len(wp),len(docs),flush=True)
for s_ in sections.values(): s_['cats']=sorted(s_['cats'])
json.dump({'arts':list(arts.values()),'cats':cats,'sections':sections,'docs':{str(k):v for k,v in docs.items()},'pdfart':pdfart,'wp':list(wp.values())},open(out,'w'),ensure_ascii=False)
print('DONE',len(arts),len(wp),len(docs),len(cats),len(sections),len(pdfart))
