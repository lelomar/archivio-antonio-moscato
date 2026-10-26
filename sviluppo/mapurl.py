# Archivio Antonio Moscato – prima versione di Leonardo Lomartire (2026) – GPL-3.0 con attribuzione, vedi LICENZA.md
import json,hashlib,re,sys,os,collections,urllib.parse
root=sys.argv[1]
WORK=os.environ.get('MOSCATO_WORK',os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else '.')
cdx=json.load(open(os.path.join(root,'.cdx.json')))
def local(url):
    u=re.sub(r'^https?://[^/]+','',url)
    raw=u.encode('latin1','ignore') if False else u
    # percent-decode repeatedly (bytes)
    b=raw.encode('utf-8')
    while True:
        d=re.sub(rb'%([0-9A-Fa-f]{2})',lambda m:bytes([int(m.group(1),16)]),b)
        if d==b: break
        b=d
    s=b.decode('utf-8','ignore')
    s=s.replace('<!--','')
    s=re.sub(r'[\x00-\x1f]','',s)
    path,_,q=s.partition('?')
    if q:
        dg=hashlib.sha256(q.encode('utf-8')).hexdigest()[:12]
        last=path.rsplit('/',1)[-1]
        if '.' in path:
            pre,_,post=path.rpartition('.')
            path=f"{pre}__q{dg}.{post}"
        else: path=f"{path}__q{dg}"
    path=re.sub('/+','/',path).lstrip('/')
    path='/'.join(re.sub(r'[:*?"<>|\\]',lambda m:'%'+format(ord(m.group()),'X'),seg) or '_' for seg in path.split('/'))
    if path=='' : path='index.html'
    return path
m={}
for ts,url in cdx:
    lp=local(url)
    cand=[lp, lp+'/index.html', lp.rstrip('/')+'/index.html']
    for c in cand:
        if os.path.isfile(os.path.join(root,c)):
            m.setdefault(c,set()).add(url); break
json.dump({k:sorted(v) for k,v in m.items()},open(os.path.join(WORK,'map.json'),'w'),ensure_ascii=False)
allf=set()
for dp,dn,fn in os.walk(root):
    for f in fn: allf.add(os.path.relpath(os.path.join(dp,f),root))
print('cdx',len(cdx),'mapped files',len(m),'total files',len(allf))
opts=collections.Counter()
for k,v in m.items():
    for u in v:
        q=urllib.parse.parse_qs(urllib.parse.urlparse(u).query)
        opts[(q.get('option',['-'])[0],q.get('view',q.get('task',['-']))[0])]+=1
for k,c in opts.most_common(25): print(c,k)
