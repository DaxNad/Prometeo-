from app.security.api_key_auth import install_auth
from app.api.api_auth import router as auth_router
from app.api.routes.dev_executor import router as dev_executor_router
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, PlainTextResponse, Response
from fastapi.staticfiles import StaticFiles

from .api.agent_runtime import router as agent_runtime_router
from .api.mobile_ui import router as mobile_ui_router
from .api.api_planner import router as planner_router
from .api.devos import router as dev_router
from .api.devos_status import router as devos_status_router
from .api.events import router as events_router
from .api.postgres_probe import router as postgres_probe_router
from .api.production_events import router as production_events_router
from .api.routes.dev_db_init import router as dev_db_init_router
from .api.state import router as state_router
from .api.ai_state import router as ai_state_router
from .api.ai import router as ai_router
from .api.real_ingest import router as real_ingest_router
from .api.tl import router as tl_router
from .api.tl_chat import router as tl_chat_router
from .api_dashboard import router as dashboard_router
from .api_production import router as production_router
from .api_search import router as search_router
from .api_signals import router as signals_router
from .api_smf import router as smf_router
from .config import settings
from .db import current_backend, init_db, probe_postgres

BASE_DIR = Path(__file__).resolve().parent.parent
UI_DIR = BASE_DIR / "ui"
FRONTEND_DIR = BASE_DIR.parent / "frontend"
FRONTEND_DIST_DIR = FRONTEND_DIR / "dist"

app = FastAPI(
    title="PROMETEO CORE",
    version=settings.version,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

startup_db_init_ok = False
startup_db_init_error = None


@app.on_event("startup")
def startup_event() -> None:
    global startup_db_init_ok, startup_db_init_error
    try:
        init_db()
        # Se siamo su Postgres, garantiamo anche lo schema 'events' legacy
        # usato da sequence planner e machine-load per le segnalazioni operative.
        try:
            if settings.postgres_configured:
                from .repositories.postgres_events_repository import PostgresEventsRepository

                PostgresEventsRepository().ensure_schema()
        except Exception as e:
            # Non blocca l'avvio: gli endpoint gestiranno con fallback
            print(f"EVENTS schema ensure skipped: {e}")
        startup_db_init_ok = True
        startup_db_init_error = None
        print("DB INIT OK")
    except Exception as e:
        startup_db_init_ok = False
        startup_db_init_error = str(e)
        print(f"DB INIT ERROR: {e}")


@app.get("/")
def root():
    dist_index = FRONTEND_DIST_DIR / "index.html"
    if dist_index.exists():
        return FileResponse(dist_index)

    ui_index = UI_DIR / "index.html"
    if ui_index.exists():
        return FileResponse(ui_index)

    return {
        "service": settings.service_name,
        "version": settings.version,
    }


@app.get("/health")
def health():
    postgres_probe = {"reachable": False, "message": "probe skipped"}
    try:
        postgres_probe = probe_postgres()
    except Exception as e:
        postgres_probe = {"reachable": False, "message": str(e)}

    db_backend = current_backend()
    events_create_status = "secondary_not_aligned_on_current_backend"
    if startup_db_init_ok and db_backend in {"sqlite", "postgres"}:
        events_create_status = "secondary_aligned_available"

    return {
        "ok": True,
        "service": settings.service_name,
        "version": settings.version,
        "ui_available": UI_DIR.exists() or FRONTEND_DIST_DIR.exists(),
        "database_configured": settings.database_configured,
        "db_backend": db_backend,
        "postgres_configured": settings.postgres_configured,
        "postgres_reachable": postgres_probe["reachable"],
        "postgres_message": postgres_probe["message"],
        "startup_db_init_ok": startup_db_init_ok,
        "startup_db_init_error": startup_db_init_error,
        "primary_operational_flow": "/production/order",
        "events_create_status": events_create_status,
        "agent_runtime_enabled": True,
    }


@app.get("/ping")
def ping():
    return {"status": "ok"}


@app.head("/ping")
def ping_head():
    return Response(status_code=200)


@app.get("/robots.txt", response_class=PlainTextResponse)
def robots_txt():
    return "User-agent: *\nDisallow:\n"


@app.get("/mobile")
def mobile():
    return {
        "ui": "prometeo-tl-mobile",
        "entry": "http://localhost:3000",
        "description": "Interfaccia Team Leader mobile",
        "recommended_views": [
            "/production/sequence",
            "/production/turn-plan",
            "/production/machine-load",
            "/agent-runtime/summary"
        ]
    }


app.include_router(dev_router)
app.include_router(search_router)
app.include_router(events_router)
app.include_router(state_router)
app.include_router(postgres_probe_router)
app.include_router(smf_router)
app.include_router(production_router)
app.include_router(planner_router)
app.include_router(dashboard_router)
app.include_router(production_events_router)
app.include_router(devos_status_router)
app.include_router(dev_db_init_router)
app.include_router(agent_runtime_router)
app.include_router(mobile_ui_router)
app.include_router(signals_router)
app.include_router(dev_executor_router)
app.include_router(ai_state_router)
app.include_router(ai_router)
app.include_router(real_ingest_router)
app.include_router(tl_router)
app.include_router(tl_chat_router)

install_auth(app)
app.include_router(auth_router)

if UI_DIR.exists():
    app.mount("/ui", StaticFiles(directory=str(UI_DIR)), name="ui")

if FRONTEND_DIST_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST_DIR), html=True), name="frontend_dist")
elif FRONTEND_DIR.exists():
    app.mount("/frontend", StaticFiles(directory=str(FRONTEND_DIR)), name="frontend")
