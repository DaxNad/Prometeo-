import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Nota: evitiamo di fallire all'import se DATABASE_URL non è impostata.
# In assenza di variabile, usiamo SQLite locale dal config dell'app.
try:
    from app.config import settings
except Exception:
    settings = None  # fallback prudente durante import parziali

RAW_DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

if RAW_DATABASE_URL.startswith("postgres://"):
    RAW_DATABASE_URL = RAW_DATABASE_URL.replace("postgres://", "postgresql://", 1)

if RAW_DATABASE_URL:
    DATABASE_URL = RAW_DATABASE_URL
else:
    # Fallback stabile per test e ambienti dev senza Postgres
    sqlite_path = getattr(settings, "sqlite_path", None)
    if sqlite_path is not None:
        DATABASE_URL = f"sqlite:///{sqlite_path}"
        SQLITE_CONNECT_ARGS = {"check_same_thread": False}
    else:
        # Ripiego estremo in memoria (raro): mantiene import non-bloccante
        DATABASE_URL = "sqlite+pysqlite:///:memory:"
        SQLITE_CONNECT_ARGS = {"check_same_thread": False}

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    # Necessario per SQLite quando usato in app/test multi-thread
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    future=True,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True,
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
