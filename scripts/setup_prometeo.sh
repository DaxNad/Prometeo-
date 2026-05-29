#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SMF_ROOT="$ROOT/data/local_smf"

echo "== PROMETEO bootstrap =="

echo "repo root: $ROOT"
echo "cartelle locali"
mkdir -p "$ROOT/.codex"
mkdir -p "$ROOT/data/local_reports/session_memory"
mkdir -p "$SMF_ROOT/backup"

echo "virtualenv python"
cd "$ROOT"

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

source .venv/bin/activate

pip install --upgrade pip
if [ -f "$ROOT/backend/requirements.txt" ]; then
    pip install -r "$ROOT/backend/requirements.txt"
else
    pip install fastapi uvicorn sqlalchemy psycopg2-binary python-dotenv pyyaml
fi

echo "dipendenze frontend"
if [ -f "$ROOT/frontend/package.json" ] && [ ! -d "$ROOT/frontend/node_modules" ]; then
    (cd "$ROOT/frontend" && npm install)
else
    echo "frontend node_modules presente o package.json mancante: skip npm install"
fi

echo "postgres locale"
brew services start postgresql@16 || true

if ! psql -lqt | cut -d \| -f 1 | grep -qw prometeo; then
    createdb prometeo || true
fi

echo "file .env base"
if [ ! -f "$ROOT/.env" ]; then
cat <<ENV > .env
APP_ENV=development
DATABASE_URL=postgresql://localhost/prometeo
PROMETEO_DB_BACKEND=postgres
API_V1_PREFIX=/api/v1
ENV
fi

echo "struttura completata"
echo "PROMETEO pronto"
echo "Prossimi comandi: make run, poi make doctor"
