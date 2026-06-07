#!/bin/bash
set -euo pipefail

PROJECT_ROOT="${PROMETEO_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"

IMAGE_PATH="${1:-}"

if [ -z "$IMAGE_PATH" ]; then
  echo "USO: ${PROJECT_ROOT}/tools/ocr/run_ocr_001.sh /percorso/immagine.png"
  exit 2
fi

if [ ! -f "$IMAGE_PATH" ]; then
  echo "ERRORE: file non trovato: $IMAGE_PATH"
  exit 1
fi

STAMP="$(date +%Y%m%d_%H%M%S)"
OUT="${PROJECT_ROOT}/data/local_reports/ocr_001/ocr_preview_${STAMP}.json"

swift ${PROJECT_ROOT}/tools/ocr/ocr_vision.swift "$IMAGE_PATH" > "$OUT"

echo "OCR preview creato:"
echo "$OUT"
