# Confronto documentale con la Wayback Machine

Questo rapporto misura quanto la ricostruzione è fedele alle pagine originali. Su 200 testi estratti a caso, con un campionamento stratificato per anno (seme 1938, quindi ripetibile da chiunque), il testo di ogni articolo ricostruito è stato confrontato parola per parola con la pagina originale salvata dalla Wayback Machine.

## Risultato

In media la ricostruzione conserva il **99.92%** delle parole dell'originale (valore minimo 98.78%), e il 54.5% dei testi è identico all'originale. La ricostruzione non aggiunge nulla: le parole assenti nell'originale sono lo 0.13%. I titoli coincidono in 200 casi su 200.

Le sole differenze riscontrate sono le scritte dei pulsanti di condivisione («Facebook») presenti nell'originale di due articoli del blog e assenti nella ricostruzione: nessuna parola dei testi è andata persa.

## Che cosa è stato tolto di proposito

La ricostruzione elimina dall'originale, e il confronto quindi non conta come perdite: i pulsanti di condivisione sui social, la navigazione «precedente / successivo», gli strumenti di stampa e invio, e il codice di stile che Microsoft Word inseriva nei testi incollati («Style Definitions»). Nessuno di questi elementi fa parte del testo di Moscato.

## Limiti

Il confronto verifica che la ricostruzione non abbia alterato i testi rispetto alle copie della Wayback Machine, che sono la sua fonte. Non può dire nulla sulle pagine che la Wayback Machine non ha mai salvato, né sui documenti allegati, il cui testo è estratto da file Word, RTF e PDF. Il controllo sulle copie online, che riscarica dalla Wayback Machine una parte del campione e ne confronta l'impronta SHA-256 con i file usati, si fa con `sviluppo/verifica_wayback.py` e salva il risultato in `verifica-wayback.json`.

## Controllo sulle copie online

Il 27 ottobre 2026, 29 pagine originali del campione sono state riscaricate dalla Wayback Machine e confrontate con i file usati per la ricostruzione. 23 sono identiche byte per byte; le altre differiscono solo nel contorno della pagina (menu, banner, contatori), perché la Wayback Machine conserva più copie della stessa pagina salvate in giorni diversi. Il testo degli articoli è identico in 29 casi su 29. Il dettaglio è in `verifica-wayback.json`.

Distribuzione del campione per anno: 2001: 1, 2004: 2, 2005: 1, 2006: 1, 2009: 6, 2010: 14, 2011: 18, 2012: 27, 2013: 25, 2014: 24, 2015: 27, 2016: 15, 2017: 12, 2018: 9, 2019: 6, 2020: 6, 2021: 6.

Il dettaglio testo per testo è in `confronto-wayback.csv`; i valori complessivi in `confronto-wayback.json`.
