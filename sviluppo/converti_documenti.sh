#!/bin/bash
# Estrae il testo dei PDF e converte DOC/RTF/DOCX in HTML per le pagine di lettura.
# Uso: bash converti_documenti.sh <cartella_del_sito_generato>
# Richiede: pdftotext (poppler) e LibreOffice (soffice).
set -e
SITE="${1:?indica la cartella del sito, es. ../SITO_MOSCATO}"
HERE="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$HERE/dconv/txt" "$HERE/dconv/html"
cd "$SITE/documenti/file"
for f in *; do
  b="${f%.*}"; e="$(echo "${f##*.}" | tr A-Z a-z)"
  if [ "$e" = pdf ]; then pdftotext -enc UTF-8 "$f" "$HERE/dconv/txt/$b.txt" 2>/dev/null || true
  else soffice --headless --convert-to "html:XHTML Writer File:UTF8" --outdir "$HERE/dconv/html" "$f" >/dev/null 2>&1 || true; fi
done
echo "Fatto: $(ls "$HERE/dconv/txt" | wc -l) PDF e $(ls "$HERE/dconv/html" | wc -l) documenti convertiti."
