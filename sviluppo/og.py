# Genera le immagini di condivisione (Open Graph) 1200x630 nella grafica «Manifesto»
import os,sys
from PIL import Image,ImageDraw,ImageFont
OUT=sys.argv[1]; FD=os.path.join(OUT,'assets','fonts')
S=2; W,H=1200*S,630*S
RED=(196,22,28); INK=(22,22,22); WHITE=(255,255,255); PINK=(255,214,214)
def archivo(size,wght=900,wdth=62):
    f=ImageFont.truetype(os.path.join(FD,'archivo-latin-wdth-normal.woff2'),size*S); f.set_variation_by_axes([wght,wdth]); return f
def literata(size,italic=True,wght=400):
    f=ImageFont.truetype(os.path.join(FD,'literata-latin-opsz-%s.woff2'%('italic' if italic else 'normal')),size*S); f.set_variation_by_axes([min(72,size),wght]); return f
def base():
    im=Image.new('RGB',(W,H),RED); d=ImageDraw.Draw(im)
    d.rectangle([0,500*S,W,H],fill=INK)
    return im,d
def footer(d,left):
    d.text((70*S,532*S),left,font=archivo(30,800,80),fill=WHITE)
    d.text((70*S,574*S),'lelomar.github.io/archivio-antonio-moscato',font=archivo(21,500,100),fill=(200,200,196))
    d.text((1130*S,574*S),'Antonio Moscato · Roma 1938 – 2026',font=archivo(21,500,100),fill=(200,200,196),anchor='ra')
def save(im,name):
    im=im.resize((1200,630),Image.LANCZOS); im.save(os.path.join(OUT,'assets',name),optimize=True)
im,d=base()
d.text((70*S,34*S),'Archivio ritrovato, 2009–2021',font=archivo(24,700,85),fill=PINK)
d.text((64*S,58*S),'MOVIMENTO',font=archivo(196),fill=WHITE)
d.text((64*S,228*S),'OPERAIO',font=archivo(196),fill=WHITE)
d.text((70*S,418*S),'Il sito di Antonio Moscato, ricostruito',font=literata(40),fill=WHITE)
footer(d,'2.929 articoli · 180 documenti su 247 · ricerca a testo pieno')
save(im,'og-archivio.png')
im,d=base()
d.text((70*S,34*S),'Un archivio salvato',font=archivo(24,700,85),fill=PINK)
d.text((64*S,58*S),'SONO RIMASTO',font=archivo(176),fill=WHITE)
d.text((64*S,212*S),'SEDUTO',font=archivo(176),fill=WHITE)
d.text((70*S,392*S),'Il sito di Antonio Moscato, storico del movimento operaio,',font=literata(30),fill=WHITE)
d.text((70*S,432*S),'ricostruito dopo la sua scomparsa da un suo studente',font=literata(30),fill=WHITE)
footer(d,'di Leonardo Lomartire')
save(im,'og-progetto.png')
print('ok og')
