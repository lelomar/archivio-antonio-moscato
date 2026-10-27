# Il modello dei dati: dal sito originale alla pagina dell'archivio

Fra un articolo che Antonio Moscato pubblicava sul suo sito e la pagina che si legge oggi in questo archivio ci sono quattro passaggi, e ognuno può introdurre una differenza. Per questo ogni testo è descritto non come un oggetto solo, ma come una catena di oggetti distinti, ciascuno con il suo identificativo, la sua impronta digitale e un legame esplicito con quello da cui deriva. Chi studia un testo può così sapere esattamente che cosa ha davanti, e da dove viene ogni parola.

## I cinque livelli

```
AM-1871.o  originale         l'articolo pubblicato su antoniomoscato.altervista.org
    │  copia di
AM-1871.c  cattura           la copia della Wayback Machine da cui viene il testo
    │  estratto da
AM-1871.t  testo estratto    il corpo dell'articolo, tolto dalla pagina senza modificarne le parole
    │  edizione di
AM-1871.e  edizione          la pagina HTML di questo archivio, in una versione precisa
    ┆
AM-1871.i1, .i2, …  interventi   ciò che è stato fatto fra un livello e l'altro
```

**Originale** (`.o`). La pubblicazione sul sito di Moscato: indirizzo, sistema che la gestiva (Joomla per gli articoli 2009–2018 e per i documenti, WordPress per il blog 2018–2021), data di pubblicazione, autore e grado di certezza dell'attribuzione. L'originale non esiste più: lo conosciamo solo attraverso le sue copie.

**Cattura** (`.c`). La copia salvata dalla Wayback Machine dell'Internet Archive da cui il testo è stato ricostruito: data e ora della copia, indirizzo per riaprirla, nome del file scaricato e sua impronta SHA-256. Per i documenti la cattura è il file stesso (PDF, DOC, RTF) che il sito offriva in download, e dice se è integro o troncato al primo megabyte. Per i documenti mancanti la cattura è vuota: la Wayback Machine ha conservato solo la pagina che li collegava.

**Testo estratto** (`.t`). Il testo tolto dalla cattura: per gli articoli, il corpo dell'articolo separato da menu, pubblicità e pulsanti; per i documenti, il testo convertito dal PDF (con pdftotext) o dal DOC e RTF (con LibreOffice). L'impronta qui non riguarda un file ma il testo semplice, con gli spazi normalizzati: se un giorno cambia l'impaginazione di una pagina, questa impronta permette di dimostrare che le parole sono rimaste le stesse.

**Edizione** (`.e`). La pagina che si consulta, nella versione indicata dell'archivio, con la sua impronta. Ogni nuova versione dell'archivio ricalcola le impronte delle edizioni; quelle delle catture e dei testi, se nulla è cambiato, restano identiche, ed è proprio questo che le rende utili.

**Interventi** (`.i1`, `.i2`, …). Gli eventi che hanno modificato qualcosa nel passaggio da un livello all'altro, ciascuno con il tipo, una descrizione, la quantità quando si può contare, chi lo ha fatto (un programma, la Wayback Machine, il curatore, una segnalazione verificata) e i due livelli fra cui avviene. Sono di questi tipi:

| Tipo | Fra | Che cosa |
| --- | --- | --- |
| pulizia | cattura → testo | rimossi menu, script, pulsanti di condivisione, stili di Word; il testo non cambia |
| link interni | testo → edizione | collegamenti al vecchio sito ricondotti alle pagine dell'archivio |
| link interni non recuperati | testo → edizione | collegamenti a pagine non conservate, indirizzati alla Wayback Machine |
| link esterni archiviati / non archiviati | testo → edizione | collegamenti ad altri siti indirizzati alla copia d'epoca, o segnalati se non esiste |
| immagini | cattura → edizione | immagini recuperate e incluse |
| note | testo → edizione | rimandi interni (note, indici) resi funzionanti |
| attribuzione | testo → edizione | autore indicato e grado di certezza |
| data di scrittura | testo → edizione | data ricavata dal testo, quando è anteriore alla pubblicazione |
| doppione unito | originale → edizione | un articolo pubblicato due volte rinvia a una sola pagina |
| recupero mirato | originale → cattura | documento ritrovato dopo la prima ricostruzione |
| troncamento | originale → cattura | file salvato solo in parte dalla Wayback Machine |
| conversione | cattura → testo | testo ricavato da PDF, DOC o RTF |

## I file

| File | Contenuto |
| --- | --- |
| `provenienza.json` | per ogni testo e documento, i livelli con identificativi, impronte e relazioni, e l'elenco degli interventi |
| `provenienza.csv` | la stessa cosa in una riga per testo, da aprire con un foglio di calcolo |
| `eventi.csv` | un intervento per riga: identificativo, oggetto, livelli di partenza e di arrivo, tipo, descrizione, quantità, agente, data |
| `conteggi.json` | i numeri dell'archivio (articoli, documenti integri, incompleti, mancanti…), calcolati a ogni costruzione: tutte le cifre dichiarate nel sito vengono da qui |

In ogni pagina di articolo la **scheda d'archivio** mostra la stessa catena in forma leggibile, con gli identificativi dei livelli.

## Anche i temi hanno due livelli

Le parole chiave degli articoli seguono la stessa logica. La parola chiave originale appartiene al livello del testo: è quella che Moscato scrisse, e resta com'è, nella scheda d'archivio e in `parole-chiave-originali.csv`. Il tema appartiene all'edizione: è l'entità normalizzata a cui la parola chiave è ricondotta, con un tipo (persona, organizzazione, luogo, evento, concetto, pubblicazione) e, dove esistono, identificativi esterni (Wikidata, VIAF, SBN, GeoNames). Il passaggio dall'una all'altro è un intervento come gli altri, registrato riga per riga: tema, unificata con un'altra forma, divisa in più temi, esclusa con il motivo. In SKOS, il formato dei thesauri, le forme originali sono le `altLabel` dell'entità.

## Corrispondenze con gli standard

Il modello non inventa nulla: traduce in forma semplice concetti che archivi e biblioteche usano già.

| Qui | PREMIS 3 | PROV-O | Dublin Core |
| --- | --- | --- | --- |
| testo dell'archivio (`AM-1871`) | Intellectual Entity | Entity | — |
| originale, cattura, testo, edizione | Object (Representation / File) | Entity | `dc:source` per l'originale |
| «copia di», «estratto da», «edizione di» | relationship (derivation) | `prov:wasDerivedFrom` | `dcterms:isVersionOf` |
| intervento | Event | Activity, `prov:wasGeneratedBy` | — |
| programma, Wayback Machine, curatore | Agent | Agent | `dc:contributor` |
| impronta SHA-256 | fixity | — | — |

## Che cosa il modello non dice

L'originale non è mai stato visto: lo ricostruiamo dalle copie. Quando di una pagina esistevano più copie, è stata usata la più recente prima del novembre 2021, data in cui i vecchi indirizzi cominciano a rimandare al nuovo blog; il [confronto documentale](confronto-wayback.md) verifica su un campione che la copia indicata e il file usato coincidano. L'impronta della cattura riguarda il file scaricato con lo strumento di download, che la Wayback Machine serve con lievi differenze di codice rispetto alla copia che si apre nel browser: per questo il confronto è fatto sul testo, oltre che sui byte.
