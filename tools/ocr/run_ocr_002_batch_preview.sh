#!/bin/bash
set -euo pipefail

OUT_DIR="/Users/davidepiangiolino/PROMETEO/data/local_reports/ocr_002"
mkdir -p "$OUT_DIR"

FILES=(
"/Users/davidepiangiolino/PROMETEO/specs_finitura/50036/50036_A1675009702_rev4.png"
"/Users/davidepiangiolino/PROMETEO/specs_finitura/12056/12056_A2145013001_rev10.png"
"/Users/davidepiangiolino/PROMETEO/specs_finitura/12066/12066_A2145013301_rev13.png"
"/Users/davidepiangiolino/PROMETEO/specs_finitura/12102/12102_A2368305500_rev9.png"
"/Users/davidepiangiolino/PROMETEO/specs_finitura/50034/50034_A1675017504_rev4.png"
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

  swift /Users/davidepiangiolino/PROMETEO/tools/ocr/ocr_vision.swift "$IMG" > "$OCR_JSON"

  /Users/davidepiangiolino/PROMETEO/tools/ocr/parse_ocr_spec_001.py "$OCR_JSON" >/dev/null

  echo "OK: ${OCR_JSON}"
done

echo
echo "DONE OCR_002 preview."
echo "Structured files:"
ls -1 "$OUT_DIR"/*_structured.json
