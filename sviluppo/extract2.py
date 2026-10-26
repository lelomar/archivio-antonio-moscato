# Archivio Antonio Moscato – prima versione di Leonardo Lomartire (2026) – GPL-3.0 con attribuzione, vedi LICENZA.md
import os,re,json,sys,urllib.parse,html,collections
from bs4 import BeautifulSoup
WORK=os.environ.get('MOSCATO_WORK',os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else '.')
import warnings; warnings.filterwarnings('ignore')
root=sys.argv[1]
M=json.load(open(os.path.join(WORK,'map.json')))
def qs(u): return urllib.parse.parse_qs(urllib.parse.urlparse(html.unescape(u)).query)
def num(x):
    m=re.match(r'\s*(\d+)',x or ''); return int(m.group(1)) if m else None
catv=collections.defaultdict(collections.Counter); secv=collections.defaultdict(collections.Counter)
dmcat={}; dmsub=collections.defaultdict(set); dmdocs={}; menus=collections.Counter()
for rel,urls in M.items():
    q=qs(urls[0])
    s=open(os.path.join(root,rel),'rb').read().decode('utf-8','ignore')
    if not s.lstrip().startswith('<') : continue
    if 'ja-content' not in s and 'dm_' not in s: continue
    soup=BeautifulSoup(s,'lxml')
    for ul in soup.select('ul.menu'):
        for a in ul.find_all('a',href=True):
            qa=qs(a['href']); t=a.get_text(' ',strip=True)
            if not t: continue
            if qa.get('view')==['category']: catv[num(qa.get('id',[''])[0])][t]+=1
            if qa.get('view')==['section']: secv[num(qa.get('id',[''])[0])][t]+=1
            menus[(t,a['href'][-90:])]+=1
    if 'cat_view' in q.get('task',[]) :
        g=num(q.get('gid',[''])[0]); nm=soup.select_one('.dm_cat .dm_name')
        if g is not None and nm: dmcat.setdefault(g,nm.get_text(' ',strip=True))
        for a in soup.select('#dm_cats a[href*="cat_view"], .dm_row a[href*="cat_view"]'):
            sg=num(qs(a['href']).get('gid',[''])[0])
            if sg and sg!=g: dmsub[g].add(sg); dmcat.setdefault(sg,a.get_text(' ',strip=True))
        for nm in soup.select('#dm_docs a.dm_name[href*="gid="]'):
            dg=num(qs(nm['href']).get('gid',[''])[0])
            box=nm.find_parent('div'); desc=box.find_next_sibling('div',class_='dm_description') if box else None
            dt=box.select_one('.dm_date') if box else None
            tip=nm.find('span',title=True)
            dmdocs.setdefault(dg,{'cat':g,'title':nm.get_text(' ',strip=True),'tip':tip['title'] if tip else '',
              'desc':desc.decode_contents() if desc else '','date':dt.get_text(strip=True) if dt else ''})
    if q.get('option')==['com_docman'] and not q.get('task') or q.get('task')==['']:
        for a in soup.select('a[href*="cat_view"]'):
            sg=num(qs(a['href']).get('gid',[''])[0]); t=a.get_text(' ',strip=True)
            if sg and t: dmsub[0].add(sg); dmcat.setdefault(sg,t)
out={'catnames':{k:v.most_common(1)[0][0] for k,v in catv.items() if k},'secnames':{k:v.most_common(1)[0][0] for k,v in secv.items() if k},
     'dmcat':dmcat,'dmsub':{k:sorted(v) for k,v in dmsub.items()},'dmdocs':dmdocs}
json.dump(out,open(os.path.join(WORK,'data2.json'),'w'),ensure_ascii=False)
print(json.dumps({k:out[k] for k in ['catnames','secnames','dmcat','dmsub']},ensure_ascii=False,indent=0)[:5000]); print('dmdocs',len(dmdocs))
print([m for m,c in menus.most_common(60)])
