# Movimento operaio – La pagina di Antonio Moscato

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23670900.svg)](https://doi.org/10.5281/zenodo.23670900)

**Archivio ricostruito del sito di Antonio Moscato (Roma 1938 – 2026), storico del movimento operaio**

🔗 Consultabile online: **https://lelomar.github.io/archivio-antonio-moscato/**

Il sito `antoniomoscato.altervista.org` (2009–2021) raccoglieva gli articoli, le polemiche e i saggi
di Antonio Moscato, per decenni docente di Storia del movimento operaio all'università di Lecce.
Dopo la sua chiusura è stato ricostruito nell'ottobre 2026, a partire dalle copie conservate
dall'Internet Archive, come archivio statico che funziona **senza server e senza internet**.

- 2.928 articoli (2009–2021), divisi nelle rubriche originali
- 180 dei 247 documenti di *I grandi nodi del Novecento*, con pagine di lettura nel browser
- ricerca a testo pieno su articoli e documenti, con filtri per rubrica, periodo, tema e lingua
- 732 temi ricavati dalle parole chiave originali, cronologia anno per anno

🔖 **Citazione permanente:** DOI [10.5281/zenodo.23670900](https://doi.org/10.5281/zenodo.23670900) (Zenodo, CERN) — oppure il pulsante «Cite this repository».

💾 **Copia di sicurezza:** [Internet Archive](https://archive.org/details/archivio-antonio-moscato) — archivio completo in ZIP, da scaricare e conservare.

📚 **Documentazione completa:** [wiki del progetto](https://github.com/lelomar/archivio-antonio-moscato/wiki) — consultazione, ricostruzione, modifica, dati, documenti mancanti.

La storia del progetto, chi era Antonio Moscato e l'elenco dei documenti ancora da ritrovare sono
nella pagina [`progetto.html`](progetto.html).

> **Prima versione a cura di [Leonardo Lomartire](https://lelomar.substack.com)**, ottobre 2026.
> Chi riutilizza il progetto deve mantenere questi crediti: vedi [CREDITI.md](CREDITI.md).

---

## Indice

1. [Consultare l'archivio](#1-consultare-larchivio)
2. [Struttura delle cartelle](#2-struttura-delle-cartelle)
3. [Modificare l'archivio](#3-modificare-larchivio)
4. [Ricostruire tutto da zero](#4-ricostruire-tutto-da-zero)
5. [Pubblicare una propria copia](#5-pubblicare-una-propria-copia)
6. [Contribuire](#6-contribuire)
7. [Crediti e licenze](#7-crediti-e-licenze)

---

## 1. Consultare l'archivio

### Online
Basta aprire https://lelomar.github.io/archivio-antonio-moscato/

### Offline, sul proprio computer
1. In questa pagina di GitHub premi **Code → Download ZIP** (circa 170 MB).
2. Decomprimi l'archivio.
3. Apri il file **`index.html`** con un doppio clic.

Funziona con Chrome, Firefox, Safari ed Edge recenti, senza installare nulla. La cartella si può
copiare così com'è su una **chiavetta USB**, un DVD o il disco di una biblioteca.

La prima ricerca a testo pieno di ogni sessione carica un indice di circa 50 MB, diviso in cinque
file: su computer lenti può impiegare qualche secondo.

### Offline con un piccolo server locale (facoltativo)
Alcuni browser applicano restrizioni ai file aperti con `file://` (per esempio sull'anteprima dei PDF).
In quel caso si può avviare un server locale dalla cartella dell'archivio:

```bash
cd archivio-antonio-moscato
python3 -m http.server 8000
```
e aprire http://localhost:8000 nel browser.

### Con git
```bash
git clone https://github.com/lelomar/archivio-antonio-moscato.git
```

---

## 2. Struttura delle cartelle

```
index.html            home
progetto.html         presentazione del progetto, documenti mancanti, codice e licenze
attualita.html        le rubriche
temi.html             indice dei temi          → temi/<tema>.html
anni.html             cronologia               → anni/<anno>.html
cerca.html            ricerca a testo pieno
articoli/<id>.html    un articolo per pagina (id = numero dell'articolo nel sito originale)
categorie/c<id>.html  una pagina per rubrica
documenti/            "I grandi nodi del Novecento"
  index.html, cat<id>.html   sezioni
  testo/<gid>.html           pagine di lettura dei documenti
  file/                      file originali (PDF, DOC, RTF)
assets/
  stile.css           tutto l'aspetto grafico (tema chiaro e scuro)
  sito.js             funzioni comuni: filtri, dimensione del testo, finestra dei PDF
  cerca.js            motore di ricerca
  meta.js             dati di titoli, date, rubriche, temi (usati da ricerca e home)
  testi-1…5.js        testo completo di articoli e documenti per la ricerca
  img/                immagini recuperate
sviluppo/             programmi che generano il sito (vedi sotto)
```

Tutto è HTML, CSS e JavaScript scritti a mano: nessun framework, nessuna dipendenza esterna,
nessun cookie, nessun tracciamento, nessuna risorsa caricata da altri siti.

---

## 3. Modificare l'archivio

### Piccole correzioni (aspetto, ricerca)
- **Grafica**: modifica `assets/stile.css`. I colori sono variabili in cima al file (`--red`, `--bg`…),
  con una seconda serie per il tema scuro.
- **Ricerca**: `assets/cerca.js`.
- **Comportamenti comuni** (filtri, finestra dei PDF, dimensione del carattere): `assets/sito.js`.

Queste modifiche hanno effetto subito: ricarica la pagina nel browser.

### Correzioni ai contenuti
Le pagine HTML sono **generate** dai programmi in `sviluppo/`: una correzione fatta a mano in
`articoli/1234.html` funziona, ma verrebbe sovrascritta alla ricostruzione successiva.
Per modifiche durature:

- **unire due temi** o cambiarne il nome visualizzato → `sviluppo/temi_alias.json`
  (`alias`: variante → forma canonica; `display`: nome mostrato);
- **testo della pagina del progetto** → `sviluppo/progetto.html`;
- **descrizioni delle rubriche** → dizionario `CATDESC` in `sviluppo/build2.py`;
- **un documento ritrovato** → vedi [Contribuire](#6-contribuire);
- poi ricostruisci il sito (sezione 4, passo 5).

---

## 4. Ricostruire tutto da zero

Serve solo se vuoi rigenerare le pagine o rifare il recupero dall'Internet Archive.

### Requisiti
- Python 3.9 o superiore, con `pip install -r sviluppo/requirements.txt` (BeautifulSoup e lxml)
- per convertire i documenti: **LibreOffice** e **pdftotext** (pacchetto *poppler*:
  `brew install poppler` su Mac, `apt install poppler-utils` su Linux)
- per riscaricare l'archivio: Ruby e [wayback-machine-downloader](https://github.com/StrawberryMaster/wayback-machine-downloader)

### Passi

```bash
# 1. scaricare tutte le copie del vecchio sito (circa 1 GB, può richiedere ore)
gem install wayback_machine_downloader_straw
wayback_machine_downloader antoniomoscato.altervista.org -d ./scaricato -c 2

cd sviluppo

# 2. associare i file scaricati (nomi cifrati) agli indirizzi originali → map.json
python3 mapurl.py ../scaricato

# 3. estrarre articoli, date, rubriche e documenti → data.json, data2.json
python3 extract.py ../scaricato data.json
python3 extract2.py ../scaricato

# 4. generare il sito una prima volta, poi convertire i documenti per le pagine di lettura
mkdir -p ../sito/assets && cp ../assets/{stile.css,sito.js,cerca.js} ../sito/assets/
python3 build2.py ../scaricato ../sito
bash converti_documenti.sh ../sito

# 5. rigenerare il sito completo (anche dopo ogni modifica ai contenuti)
python3 build2.py ../scaricato ../sito
```

Note:
- `data.json` (oltre 100 MB) non è nel repository per i limiti di GitHub: si rigenera al passo 3.
  `map.json`, `data2.json` e `temi_alias.json` invece ci sono.
- Le cartelle facoltative `recupero/` (dentro la cartella scaricata) contengono i documenti
  recuperati in un secondo momento: `rapporto.json` e i file in `recupero/file/`
  vengono integrati automaticamente da `build2.py`.
- Variabile d'ambiente `MOSCATO_WORK`: cartella dei dati di lavoro (predefinita: `sviluppo/`).

---

## 5. Pubblicare una propria copia

**GitHub Pages** (gratuito):
1. Premi **Fork** in questa pagina.
2. Nel tuo fork: **Settings → Pages → Branch: `main`, cartella `/ (root)` → Save**.
3. Dopo qualche minuto il sito è su `https://<tuo-utente>.github.io/archivio-antonio-moscato/`.

**Altri hosting statici** (Netlify, Cloudflare Pages, il server di un'associazione, un hosting
qualsiasi): basta caricare l'intera cartella. Non servono PHP, database o configurazioni.
Per Netlify e Cloudflare usa i loro strumenti da riga di comando (`netlify deploy`, `wrangler pages deploy`):
il caricamento trascinando la cartella ha limiti sul numero e sul peso dei file.

**Su supporto fisico**: copia la cartella su chiavetta, DVD o disco e indica di aprire `index.html`.

In ogni caso: **gratuitamente, senza scopo di lucro, mantenendo i crediti** (sezione 7).

---

## 6. Contribuire

- **Hai uno dei documenti mancanti?** È il contributo più prezioso. L'elenco completo è nella pagina
  [progetto.html](progetto.html#mancanti). Apri una *issue* allegando il file, oppure scrivi a
  lelomar@gmail.com.
- **Hai trovato un errore** (refuso, data, rubrica sbagliata, temi da unire)? Apri una *issue*
  o proponi una *pull request* modificando i file in `sviluppo/`.
- **Vuoi migliorare grafica o ricerca?** *Pull request* su `assets/`.

Aggiungi il tuo nome nella sezione «Contributi successivi» di [CREDITI.md](CREDITI.md).

---

## 7. Crediti e licenze

**Prima versione: Leonardo Lomartire, ottobre 2026** — [lelomar.substack.com](https://lelomar.substack.com).
Il lavoro tecnico è stato svolto con l'assistenza di Claude (Anthropic).

| Componente | Licenza |
| --- | --- |
| Codice (HTML dei modelli, CSS, JavaScript, `sviluppo/`) | [GNU GPL v3](LICENSE) + obbligo di attribuzione (sez. 7b) |
| Lavoro di cura (indici, temi, struttura, testi di presentazione) | [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.it) |
| Testi originali | diritti degli autori e dei loro eredi |

**Obbligo di attribuzione.** Chi ridistribuisce o modifica il progetto deve conservare in ogni
pagina la menzione della prima versione a cura di Leonardo Lomartire, con collegamento a
https://lelomar.substack.com, la pagina `progetto.html` e il file `CREDITI.md`.
Dettagli in [LICENZA.md](LICENZA.md) e [CREDITI.md](CREDITI.md).

I testi di Antonio Moscato e degli altri autori sono riproposti gratuitamente, con finalità di
documentazione e memoria. Chi ne detiene i diritti e desidera la rimozione o la correzione di un
testo può scrivere a lelomar@gmail.com.
