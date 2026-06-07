#!/bin/bash
set -euo pipefail

IMAGE_PATH="${1:-}"

if [ -z "$IMAGE_PATH" ]; then
  echo "USO: /Users/davidepiangiolino/PROMETEO/tools/ocr/run_ocr_001.sh /percorso/immagine.png"
  exit 2
fi

if [ ! -f "$IMAGE_PATH" ]; then
  echo "ERRORE: file non trovato: $IMAGE_PATH"
  exit 1
fi

STAMP="$(date +%Y%m%d_%H%M%S)"
OUT="/Users/davidepiangiolino/PROMETEO/data/local_reports/ocr_001/ocr_preview_${STAMP}.json"

swift /Users/davidepiangiolino/PROMETEO/tools/ocr/ocr_vision.swift "$IMAGE_PATH" > "$OUT"

echo "OCR preview creato:"
echo "$OUT"
