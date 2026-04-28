# SETUP OPERATIVO MAC M4

Prerequisiti sistema
xcode-select --install

Installazione Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

Pacchetti base
brew install git python node postgresql@16 tree

Creazione struttura base
mkdir -p ~/PROMETEO
mkdir -p ~/PROMETEO/data/local_smf

Ambiente Python
cd ~/PROMETEO
python3 -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn sqlalchemy psycopg2-binary python-dotenv pyyaml

Database locale
brew services start postgresql@16
createdb prometeo

Verifica DB
psql prometeo

Avvio backend
cd ~/PROMETEO
uvicorn backend.app.main:app --reload

URL API
http://127.0.0.1:8000/docs

Frontend
cd ~/PROMETEO/frontend
npm install
npm run dev

URL frontend
http://127.0.0.1:5173
