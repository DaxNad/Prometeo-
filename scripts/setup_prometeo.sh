#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="${HOME}/PROMETEO"
SMF_ROOT="${HOME}/PROMETEO/data/local_smf"

echo "== PROMETEO bootstrap =="

echo "cartelle base"
mkdir -p "$ROOT"
mkdir -p "$ROOT/backend"
mkdir -p "$ROOT/frontend"
mkdir -p "$ROOT/docs"
mkdir -p "$ROOT/scripts"
mkdir -p "$ROOT/.codex"

mkdir -p "$SMF_ROOT"
mkdir -p "$SMF_ROOT/backup"

echo "virtualenv python"
cd "$ROOT"

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

source .venv/bin/activate

pip install --upgrade pip
pip install fastapi uvicorn sqlalchemy psycopg2-binary python-dotenv pyyaml

echo "postgres locale"
brew services start postgresql@16 || true

if ! psql -lqt | cut -d \| -f 1 | grep -qw prometeo; then
    createdb prometeo || true
fi

echo "file .env base"
if [ ! -f ".env" ]; then
cat <<ENV > .env
APP_ENV=development
DATABASE_URL=postgresql://localhost/prometeo
PROMETEO_DB_BACKEND=postgres
API_V1_PREFIX=/api/v1
ENV
fi

echo "struttura completata"
echo "PROMETEO pronto"
