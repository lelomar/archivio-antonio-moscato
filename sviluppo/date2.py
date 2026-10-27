import json,re,collections
T=json.load(open('testi_autori2.json'))
MES='gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre|enero|febrero|abril|mayo|junio|julio|septiembre|octubre|noviembre|diciembre'
Y=r"(?:19[4-9]\d|20[0-2]\d)"
DT=rf"(?:\d{{1,2}}\s+(?:{MES})\s+{Y}|(?:{MES})\s+(?:del\s+)?{Y}|\d{{1,2}}[/.]\d{{1,2}}[/.](?:19|20)?\d{{2}}|(?:primavera|estate|autunno|inverno)\s+(?:del\s+)?{Y}|{Y})"
SELF=r"(?i:quest[oa] (?:testo|articolo|saggio|intervento|scritto|lettera|relazione|nota|pezzo)|ripropon|ripubblic|riprend|ritrovat|ripesc|di allora|vecchi[oa] (?:testo|articolo|scritto)|un mio|una mia|il mio|la mia|ho scritto|avevo scritto|scrivevo|lo pubblico|ripresento)"
VERB=r"(?i:scritt[oaie]|redatt[oaie]|appars[oaie]|pubblicat[oaie]|uscit[oaie]|presentat[oaie]|pronunciat[oaie]|ho scritto|avevo scritto|scrivevo|risale)"
PA=re.compile(rf"{VERB}[^.;()]{{0,60}}?\b(?:nel|il|in|a|del|nell'|ad)\s*({DT})",re.I)
PAR=re.compile(rf"[\(\[]\s*(?:[A-ZÀ-Ý][\w' ]{{2,25}},?\s*)?({DT})\s*[\)\]]")
SIG=re.compile(rf"^(?:[A-ZÀ-Ý][\w' ]{{2,25}},\s*)?((?:\d{{1,2}}\s+)?(?:{MES})\s+{Y})\.?$",re.I)
REL=re.compile(r"(?i:scritt\w*|ho scritto|avevo scritto|scrivevo|pubblicat\w*|appars\w*)[^.;]{0,40}?\b(un|due|tre|quattro|cinque|sei|sette|otto|nove|dieci|una decina di|una quindicina di|una ventina di|vent'|trent'|quarant'|venti|trenta|quaranta|\d{1,2})\s*anni\s+fa")
NUM={'un':1,'due':2,'tre':3,'quattro':4,'cinque':5,'sei':6,'sette':7,'otto':8,'nove':9,'dieci':10,'una decina di':10,'una quindicina di':15,'una ventina di':20,"vent'":20,"trent'":30,"quarant'":40,'venti':20,'trenta':30,'quaranta':40}
def yr(s):
    m=re.search(r"(19[4-9]\d|20[0-2]\d)",s)
    if m: return int(m.group(1))
    m=re.search(r"\d{1,2}[/.]\d{1,2}[/.](\d{2,4})$",s.strip())
    if m:
        y=int(m.group(1)); return y if y>100 else (2000+y if y<30 else 1900+y)
    return None
res={}
for t in T:
    if not t['d']: continue
    py=int(t['d'][:4]); f=re.split(r"\sTags:\s",t['full'])[0]
    ps=[p[0] for p in t['ps'] if p[0]!='…']
    sents=re.split(r"(?<=[.!?])\s+",f[:2500])+re.split(r"(?<=[.!?])\s+",f[-1500:])
    best=None
    for p in ps[:3]+ps[-3:]:
        m=SIG.match(p.strip())
        if m and yr(m.group(1)) and yr(m.group(1))<py: best=('alta',m.group(1),yr(m.group(1)),'data in calce o in testa: «'+p[:80]+'»'); break
    if not best:
        for s in sents:
            m=REL.search(s)
            if m:
                n=NUM.get(m.group(1).lower(),None) or (int(m.group(1)) if m.group(1).isdigit() else None)
                if n and n>=1: best=('circa',f'circa {py-n}',py-n,'«'+s[:220]+'»'); break
            if not re.search(SELF,s): continue
            m=PA.search(s)
            if m and yr(m.group(1)) and yr(m.group(1))<py: best=('alta',m.group(1),yr(m.group(1)),'«'+s[:220]+'»'); break
            m=REL.search(s)
            if m:
                n=NUM.get(m.group(1).lower(),None) or (int(m.group(1)) if m.group(1).isdigit() else None)
                if n and n>=1: best=('circa',f'circa {py-n}',py-n,'«'+s[:220]+'»'); break
    if not best:
        for p in ps[:2]+ps[-2:]:
            m=PAR.search(p)
            if m and yr(m.group(1)) and yr(m.group(1))<py and len(p)<140 and not re.match(r'^\s*[\[(]?\d',p) and not re.search(r'http|pp?\.\s*\d|Ed\.|ed\.|[Ii]n:|ristampat|\(\d{4}\),',p): best=('media',m.group(1),yr(m.group(1)),'«'+p[:160]+'»'); break
    if best: res[t['id']]={'titolo':t['t'],'pubblicato':t['d'],'certezza':best[0],'scritto':best[1],'anno':best[2],'indizio':best[3]}
json.dump(res,open('date_scrittura.json','w'),ensure_ascii=False,indent=0)
print(len(res),collections.Counter(v['certezza'] for v in res.values()))
import random;random.seed(7)
for k in random.sample(list(res),30):
    v=res[k]; print(v['pubblicato'][:4],'→',v['scritto'],'|',v['certezza'],'|',v['titolo'][:28],'|',v['indizio'][:130])
print(res.get('1871'))
