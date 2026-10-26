# sviluppo/

Programmi che hanno ricostruito l'archivio a partire dalle copie della Wayback Machine.
Le istruzioni complete sono nel [README principale](../README.md#4-ricostruire-tutto-da-zero).

| File | Ruolo |
| --- | --- |
| `mapurl.py` | associa i file scaricati (nomi cifrati `__q…`) agli indirizzi originali → `map.json` |
| `extract.py` | estrae articoli Joomla e WordPress, date, rubriche, documenti → `data.json` |
| `extract2.py` | estrae menu, nomi delle rubriche, albero e schede dei documenti → `data2.json` |
| `build.py` | base comune: pulizia dell'HTML, riscrittura dei link, copia dei documenti |
| `build2.py` | genera tutte le pagine del sito, i temi, gli indici e i dati della ricerca |
| `converti_documenti.sh` | testo dei PDF (pdftotext) e HTML dei DOC/RTF (LibreOffice) → `dconv/` |
| `temi_alias.json` | fusioni delle varianti dei temi e nomi visualizzati |
| `progetto.html` | testo della pagina di presentazione |

Uso tipico dopo una modifica ai contenuti:

```bash
python3 build2.py <cartella_scaricata> <cartella_del_sito>
```

Codice rilasciato sotto GNU GPL v3 con obbligo di attribuzione: vedi `../LICENZA.md` e `../CREDITI.md`.
Prima versione: Leonardo Lomartire, ottobre 2026.
