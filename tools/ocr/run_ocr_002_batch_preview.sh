#!/bin/bash
set -euo pipefail

PROJECT_ROOT="${PROMETEO_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"

OUT_DIR="${PROJECT_ROOT}/data/local_reports/ocr_002"
mkdir -p "$OUT_DIR"

FILES=(
"${PROJECT_ROOT}/specs_finitura/50036/50036_A1675009702_rev4.png"
"${PROJECT_ROOT}/specs_finitura/12056/12056_A2145013001_rev10.png"
"${PROJECT_ROOT}/specs_finitura/12066/12066_A2145013301_rev13.png"
"${PROJECT_ROOT}/specs_finitura/12102/12102_A2368305500_rev9.png"
"${PROJECT_ROOT}/specs_finitura/50034/50034_A1675017504_rev4.png"
)

echo "OCR_002 batch preview"
echo "Output: $OUT_DIR"
echo

for IMG in "${FILES[@]}"; do
  if [ ! -f "$IMG" ]; then
    echo "SKIP: file non trovato: $IMG"
    continue
  fi

  BASE="$(basename "$IMG")"
  NAME="${BASE%.*}"
  OCR_JSON="$OUT_DIR/${NAME}_ocr.json"

  echo "PROCESS: $IMG"

  swift ${PROJECT_ROOT}/tools/ocr/ocr_vision.swift "$IMG" > "$OCR_JSON"

  ${PROJECT_ROOT}/tools/ocr/parse_ocr_spec_001.py "$OCR_JSON" >/dev/null

  echo "OK: ${OCR_JSON}"
done

echo
echo "DONE OCR_002 preview."
echo "Structured files:"
ls -1 "$OUT_DIR"/*_structured.json
