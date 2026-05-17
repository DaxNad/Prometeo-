#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

python3 evals/run_tl_semantic_eval.py
