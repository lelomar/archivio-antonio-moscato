# Confeziona l'archivio come pacchetto BagIt 1.0 (RFC 8493) in un file ZIP.
# Uso: python3 crea_bag.py SITO_MOSCATO destinazione.zip
# Verifica: pip install bagit && bagit.py --validate <cartella decompressa>
import os,sys,zipfile,hashlib,datetime
OUT,DEST=sys.argv[1],sys.argv[2]
NAME='archivio-antonio-moscato'
sums=[l.rstrip('\n').split('  ',1) for l in open(os.path.join(OUT,'SHA256SUMS'),encoding='utf-8')]
tot=sum(os.path.getsize(os.path.join(OUT,p)) for _,p in sums)
manifest=''.join(f'{h}  data/{p}\n' for h,p in sums)
bagit='BagIt-Version: 1.0\nTag-File-Character-Encoding: UTF-8\n'
info=f'''Source-Organization: Leonardo Lomartire (curatore)
Contact-Name: Leonardo Lomartire
Contact-Email: lelomar@gmail.com
External-Description: Movimento operaio. Il sito di Antonio Moscato (2009-2021), ricostruito. Archivio del sito antoniomoscato.altervista.org ricostruito dalle copie della Wayback Machine.
External-Identifier: https://doi.org/10.5281/zenodo.23670900
Bagging-Date: {datetime.date.today().isoformat()}
Payload-Oxum: {tot}.{len(sums)}
Bag-Software-Agent: crea_bag.py (archivio-antonio-moscato)
'''
tags={'bagit.txt':bagit,'bag-info.txt':info,'manifest-sha256.txt':manifest}
tagman=''.join(f'{hashlib.sha256(v.encode()).hexdigest()}  {k}\n' for k,v in tags.items())
with zipfile.ZipFile(DEST,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for k,v in tags.items(): z.writestr(f'{NAME}/{k}',v)
    z.writestr(f'{NAME}/tagmanifest-sha256.txt',tagman)
    for _,p in sums: z.write(os.path.join(OUT,p),f'{NAME}/data/{p}')
print('bag',len(sums),'file',tot,'byte')
