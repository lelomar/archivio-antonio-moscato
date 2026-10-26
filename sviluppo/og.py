# Genera le immagini di condivisione (Open Graph) 1200x630
import json,os,sys,re,collections
from PIL import Image,ImageDraw,ImageFont,ImageFilter
OUT=sys.argv[1]
F='/usr/share/fonts/opentype/urw-base35/'; L='/usr/share/fonts/truetype/lato/'
def f(p,s): return ImageFont.truetype(p,s)
meta=json.loads(re.sub(r'^window\.META=|;$','',open(os.path.join(OUT,'assets','meta.js')).read().strip()))
yc=collections.Counter(a[2][:4] for a in meta['arts'] if a[2][:4] and '2009'<=a[2][:4]<='2021')
years=sorted(yc)
S=2; W,H=1200*S,630*S
CREAM=(246,239,227); RED=(150,30,24); DARK=(96,16,12)
def base():
    im=Image.new('RGB',(W,H),RED); d=ImageDraw.Draw(im)
    for y in range(H):  # vertical gradient
        t=y/H; c=tuple(int(RED[i]*(1-t)+DARK[i]*t) for i in range(3)); d.line([(0,y),(W,y)],fill=c)
    return im
def histo(im,x0,y1,w,h,alpha=95,labels=True):
    ov=Image.new('RGBA',im.size,(0,0,0,0)); d=ImageDraw.Draw(ov)
    n=len(years); gap=10*S; bw=(w-gap*(n-1))/n; mx=max(yc.values())
    for i,y in enumerate(years):
        bh=h*yc[y]/mx; x=x0+i*(bw+gap)
        d.rectangle([x,y1-bh,x+bw,y1],fill=CREAM+(alpha,))
        if labels: d.text((x+bw/2,y1+12*S),"'"+y[2:],font=f(L+'Lato-Bold.ttf',15*S),fill=CREAM+(150,),anchor='mt')
    d.line([(x0,y1),(x0+w,y1)],fill=CREAM+(140,),width=2*S)
    d.text((x0+w,y1+40*S),'testi pubblicati per anno',font=f(L+'Lato-Italic.ttf',14*S),fill=CREAM+(160,),anchor='ra')
    im.paste(ov,(0,0),ov)
def spaced(d,xy,txt,font,fill,sp):
    x,y=xy
    for ch in txt: d.text((x,y),ch,font=font,fill=fill); x+=d.textlength(ch,font=font)+sp
def footer(d):
    d.line([(80*S,548*S),(1120*S,548*S)],fill=CREAM+(),width=1*S)
    d.text((80*S,568*S),'Antonio Moscato · Roma 1938 – 2026',font=f(L+'Lato-Bold.ttf',21*S),fill=CREAM)
    d.text((1120*S,568*S),'lelomar.github.io/archivio-antonio-moscato',font=f(L+'Lato-Regular.ttf',21*S),fill=CREAM,anchor='ra')
def save(im,name):
    im=im.resize((1200,630),Image.LANCZOS); im.save(os.path.join(OUT,'assets',name),optimize=True)
# 1. archivio
im=base(); histo(im,700*S,470*S,420*S,300*S)
d=ImageDraw.Draw(im)
spaced(d,(80*S,86*S),'ARCHIVIO RITROVATO · 2009–2021',f(L+'Lato-Black.ttf',19*S),CREAM,3*S)
d.text((76*S,128*S),'Movimento',font=f(F+'P052-Bold.otf',96*S),fill=CREAM)
d.text((76*S,232*S),'operaio',font=f(F+'P052-Bold.otf',96*S),fill=CREAM)
d.text((80*S,352*S),'La pagina di Antonio Moscato',font=f(F+'P052-Italic.otf',42*S),fill=CREAM)
d.text((80*S,432*S),'2.940 articoli · 180 saggi e documenti',font=f(L+'Lato-Bold.ttf',25*S),fill=CREAM)
d.text((80*S,468*S),'ricerca a testo pieno · consultabile anche offline',font=f(L+'Lato-Regular.ttf',23*S),fill=CREAM)
footer(d); save(im,'og-archivio.png')
# 2. progetto
im=base(); histo(im,700*S,470*S,420*S,300*S,alpha=70)
d=ImageDraw.Draw(im)
spaced(d,(80*S,86*S),'UN ARCHIVIO SALVATO',f(L+'Lato-Black.ttf',19*S),CREAM,3*S)
d.text((76*S,128*S),'Sono rimasto',font=f(F+'P052-Bold.otf',92*S),fill=CREAM)
d.text((76*S,228*S),'seduto',font=f(F+'P052-Bold.otf',92*S),fill=CREAM)
y=352*S
for line in ['Il sito di Antonio Moscato, storico del','movimento operaio, ricostruito dopo','la sua scomparsa da un suo studente']:
    d.text((80*S,y),line,font=f(F+'P052-Italic.otf',31*S),fill=CREAM); y+=40*S
d.text((80*S,500*S),'di Leonardo Lomartire',font=f(L+'Lato-Bold.ttf',22*S),fill=CREAM)
footer(d); save(im,'og-progetto.png')
print('ok',years,[yc[y] for y in years])
