# Registro delle versioni

Questo file elenca che cosa cambia da una versione all'altra dell'archivio *Movimento operaio. Il sito di Antonio Moscato (2009–2021), ricostruito*. Ogni versione pubblicata è depositata su Zenodo: il DOI [10.5281/zenodo.23670899](https://doi.org/10.5281/zenodo.23670899) porta sempre all'insieme delle versioni, e chi ha citato una versione precedente può ritrovarla lì com'era.

Il formato segue [Keep a Changelog](https://keepachangelog.com/it-IT/1.1.0/); i numeri di versione seguono la convenzione *maggiore.minore.correzione*.

## [Non ancora pubblicato]

Le correzioni segnalate dai lettori e approvate vengono raccolte qui fino alla versione successiva.

## [1.2.3] – 13 novembre 2026

**Un documento incompleto ora è integro.** Della *Revista R* di febbraio 2013 (gid 248, «Ecuador Revista R febrero 2013»), rivista socialista di Quito, la Wayback Machine aveva conservato solo il primo megabyte. Il file intero è stato trovato in rete (yachana.org) e confrontato byte per byte: i suoi primi 1.048.576 byte coincidono con la copia troncata, quindi è lo stesso file che il sito offriva in download. Torna integro, con pagina di lettura; la provenienza registra l'evento «completamento» con le due impronte SHA-256 e la fonte. Gli integri passano da 170 a 171, gli incompleti da 10 a 9.

**DOI dell'archivio.** L'archivio cita ora il DOI di concetto di Zenodo, 10.5281/zenodo.23670899, che porta sempre all'ultima versione e all'elenco di tutte le versioni. Fino alla 1.2.2 veniva citato 10.5281/zenodo.23670900, che è il DOI della sola versione 1.0.1: resta valido, ma rimanda a quella versione.

## [1.2.2] – 13 novembre 2026

**Documenti ritrovati grazie ai lettori.** Due documenti che l'Internet Archive non aveva mai salvato tornano nell'archivio, grazie a Silvio, che ne ha allegato una copia alle schede su GitHub il 5 novembre 2026: «Ernest Mandel - Introduzione al marxismo» (gid 221, scansione dell'edizione Datanews, Roma 1998, 128 pagine; issue #38, segnalazione S-2026-002) e «Maitan - Al termine di una lunga marcia dal PCI al PDS» (gid 212, scansione dell'edizione coop. Massari, Roma 1990, 62 pagine; issue #44, segnalazione S-2026-003). Titolo, autore ed edizione sono stati verificati sul frontespizio e corrispondono alle schede del sito originale. Non sono però i file che il sito offriva in download, che restano perduti: sono copie dello stesso testo. Per questo hanno uno stato nuovo, «ritrovato (copia fornita da un collaboratore)», distinto da «integro», e nella provenienza la cattura è descritta come «altra copia» dell'originale, con chi l'ha fornita, la data, l'allegato da cui proviene e l'impronta SHA-256 del file ricevuto. Ognuno ha la sua pagina di lettura, con il testo estratto dal riconoscimento ottico della scansione. I documenti nell'archivio passano da 180 a 182, i mancanti da 56 a 54.

**Un riferimento per un documento mancante.** Di «Vite parallele Castro-Chavez» (gid 61) Silvio ha segnalato la pubblicazione su *Limes*, consultabile solo in abbonamento (issue #29, segnalazione S-2026-004). Il riferimento è ora nella scheda e nella provenienza, come evento «riferimento bibliografico»; il file resta mancante.

**Autori.** «La politica israeliana in una intervista di Cinzia Nachira a Michel Warschawski» (AM-3195) è ora attribuito a Cinzia Nachira, autrice dell'intervista; prima era attribuito per presunzione ad Antonio Moscato. Fonte: la copia della Wayback Machine del 6 marzo 2021 dell'intervista pubblicata su rproject.it, sito da cui l'articolo dichiara di provenire. Segnalazione S-2026-001, di Leonardo, verificata dal curatore.

**Segnalazioni accolte.** Nuovo registro `dati/segnalazioni-accolte.csv` (e `.json`): ogni correzione arrivata dal pannello dei collaboratori o dalle schede su GitHub e accolta, con il riferimento, lo stato prima e dopo, la fonte, le date e il nome di chi l'ha segnalata, se ha chiesto di essere citato. Lo stesso riferimento compare nella scheda d'archivio del testo e, con la fonte, nell'evento «attribuzione» di `eventi.csv`.

## [1.2.1] – 28 ottobre 2026

### Aggiunto
- Recuperato l'articolo 12, «Benvenuti!»: la lettera con cui Moscato presentava il sito nella home page, firmata «Recanati 1 febbraio 2016». La prima estrazione non l'aveva riconosciuto perché la pagina non ha l'intestazione standard degli articoli; il testo è ripreso senza modifiche dalla copia della Wayback Machine (`sviluppo/estrai_aggiunti.py`), con scheda d'archivio e provenienza come gli altri. Gli articoli passano da 2.928 a 2.929. La lettera è riprodotta per intero in home, al posto della citazione che ne riportava la prima frase.
- In home, subito sotto l'apertura, l'effemeride del giorno: un testo pubblicato da Moscato in questa data, lo stesso per tutta la giornata, con il link agli altri testi del giorno.
- Ai file di grafica e agli script è associato un numero di versione, così dopo ogni aggiornamento i browser scaricano subito quelli nuovi.
- Nella pagina dei temi, i collegamenti per scaricare il vocabolario in CSV, JSON e SKOS, le parole chiave originali e le voci da verificare.

### Corretto
- L'immagine di condivisione dell'archivio indicava «247 documenti»: ora dice «180 documenti su 247».
- Il riquadro «Accadde oggi» della home mostrava solo la data: lo script che inserisce la data di consultazione nelle citazioni ne sovrascriveva il contenuto.

## [1.2.0] – 27 ottobre 2026

### Aggiunto
- Provenienza a livelli per ogni testo e documento: originale, cattura della Wayback Machine, testo estratto o convertito, edizione HTML e interventi, come oggetti distinti con identificativo, impronta SHA-256 e relazione con il livello da cui derivano (`dati/provenienza.json`, `dati/provenienza.csv`, `dati/eventi.csv`, `dati/MODELLO.md`). La scheda d'archivio di ogni articolo mostra la catena.
- Vocabolario dei temi a due livelli. Le parole chiave originali sono conservate intatte, articolo per articolo, con il trattamento ricevuto (`dati/parole-chiave-originali.csv`) e nella scheda d'archivio di ogni articolo. Le entità normalizzate sono classificate per tipo (persona, organizzazione, luogo, evento, concetto, pubblicazione), con identificativi Wikidata, VIAF, SBN e GeoNames dove esistono; il vocabolario si scarica anche in SKOS. L'indice dei temi si filtra per tipo, e ogni pagina di tema riporta le parole chiave originali da cui deriva.
- Elenco delle voci ambigue da verificare (`dati/vocabolario-da-verificare.csv`), segnalate anche nelle pagine dei temi.
- `dati/conteggi.json`: i numeri dell'archivio calcolati a ogni costruzione, con un controllo che ferma la costruzione se i totali non tornano e uno che segnala le cifre superate nei testi descrittivi.

### Corretto
- Vocabolario: unificate le grafie diverse dello stesso soggetto (per esempio «Art. 18» e «Articolo 18», «Trockij» e «Trotskij», «Irak» e «Iraq»); unificati i cognomi usati da soli con il nome completo quando nei testi compare una sola persona con quel cognome; divise le parole chiave che contenevano due soggetti per una virgola mancante («Tsipras Grecia»). I vecchi indirizzi delle pagine dei temi unificati rinviano a quelli nuovi.
- Conteggio dei documenti reso esplicito: 247 = 180 nell'archivio (170 integri e 10 incompleti) + 67 assenti (56 mai salvati e 11 video o audio esterni). Prima il testo poteva far credere che i 10 incompleti fossero esclusi dai 180, e la home indicava 247 documenti senza dire quanti sono consultabili.
- Nel catalogo, un documento ritrovato dopo la prima ricostruzione ma anch'esso troncato (gid 273) risultava «ritrovato» e non «incompleto»: stato del file e modo del recupero sono ora due campi distinti (`stato`, `recupero`).
- Descrizione del repository GitHub e testi di presentazione: 2.928 articoli, non 2.940 (il numero dei testi estratti prima di togliere 6 pagine di servizio e 6 doppie pubblicazioni). Nella cronaca della ricostruzione, i post WordPress già presenti sono 62, non 63.

## [1.1.0] – ottobre 2026

### Aggiunto
- Autore di ogni testo, ricavato dalle firme presenti nel testo (sigla «a.m.», nome di Moscato, righe «di…», nomi in apertura o in chiusura), con il grado di certezza dichiarato; indicazione dei testi di altri autori introdotti o commentati da Moscato.
- Pagine «Autori» e «Autori da verificare»; in ogni articolo, «Segnala una correzione» con modulo GitHub o email.
- Data di scrittura, accanto a quella di pubblicazione sul sito, per i testi che dichiarano di essere stati scritti prima.
- Scheda d'archivio in ogni articolo (identificativo, provenienza, copia della Wayback Machine usata) e citazione pronta in due formati.
- Pagina «Criteri di edizione».
- Pagina biografica «Antonio Moscato», con l'elenco delle opere e le fonti.
- Catalogo dei metadati (CSV, JSON, Dublin Core), manifesto di integrità con impronte SHA-256, confronto documentale con la Wayback Machine su 200 testi e controllo sulle copie online.
- Pacchetto di deposito in formato BagIt 1.0.
- Meta tag per Google Scholar; scheda Wikidata dell'archivio (Q141880166).
- Collegamenti alle copie d'archivio dei siti esterni citati negli articoli, scelte nei giorni in cui Moscato li citava.
- Collegamenti dei temi principali alle schede Wikidata; vocabolario dei temi esportabile.

### Modificato
- Nuova grafica, ispirata alla stampa militante (*Bandiera Rossa*, *Critica Comunista*), con caratteri inclusi nell'archivio; menu per telefono; versione da stampare; testate delle rubriche.
- Nuovo nome: «Movimento operaio. Il sito di Antonio Moscato (2009–2021), ricostruito». Il titolo del sito originale resta dove si parla del sito originale.
- Uniformate le varianti di grafia dei temi (per esempio Trotskij/Trotsky, Syriza/Siriza); i vecchi indirizzi delle pagine dei temi rinviano a quelli nuovi.

### Corretto
- Ripristinati i richiami alle note in 335 articoli, che nella ricostruzione automatica avevano perso il collegamento al testo della nota.
- Nel catalogo, la copia della Wayback Machine indicata per i vecchi indirizzi è ora l'ultima salvata prima del passaggio del sito a blog (novembre 2021), e non più una copia successiva che mostrava la home del blog.
- Pulizia dei testi: rimossi residui di codice di Word e scritte dei pulsanti di condivisione; sei pagine di servizio e sei doppioni sostituiti da rinvii.
- Accessibilità: contrasti, navigazione da tastiera, lettori di schermo.

## [1.0.1] – 26 ottobre 2026

### Aggiunto
- Deposito su Zenodo con DOI e file di citazione.

## [1.0] – 26 ottobre 2026

Prima versione: 2.928 articoli e 180 documenti ricostruiti dalle copie della Wayback Machine, ricerca a testo pieno, temi, cronologia, «Accadde oggi», consultazione anche senza internet.
