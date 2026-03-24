from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles

from .api.devos import router as dev_router
from .api.devos_status import router as devos_status_router
from .api.events import router as events_router
from .api.postgres_probe import router as postgres_probe_router
from .api.production_events import router as production_events_router
from .api.state import router as state_router
from .api_search import router as search_router
from .api_smf import router as smf_router
from .api_production import router as production_router
from .api_dashboard import router as dashboard_router
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

    return {
        "ok": True,
        "service": settings.service_name,
        "version": settings.version,
        "ui_available": UI_DIR.exists() or FRONTEND_DIST_DIR.exists(),
        "database_configured": settings.database_configured,
        "db_backend": current_backend(),
        "postgres_configured": settings.postgres_configured,
        "postgres_reachable": postgres_probe["reachable"],
        "postgres_message": postgres_probe["message"],
        "startup_db_init_ok": startup_db_init_ok,
        "startup_db_init_error": startup_db_init_error,
    }


@app.get("/ping")
def ping():
    return {"status": "ok"}


@app.head("/ping")
def ping_head():
    return Response(status_code=200)


@app.get("/mobile")
def mobile():
    mobile_file = FRONTEND_DIST_DIR / "mobile.html"
    if mobile_file.exists():
        return FileResponse(mobile_file)

    legacy_mobile = FRONTEND_DIR / "mobile.html"
    if legacy_mobile.exists():
        return FileResponse(legacy_mobile)

    return Response(status_code=404)


app.include_router(dev_router)
app.include_router(search_router)
app.include_router(events_router)
app.include_router(state_router)
app.include_router(postgres_probe_router)
app.include_router(smf_router)
app.include_router(production_router)
app.include_router(dashboard_router)
app.include_router(production_events_router)
app.include_router(devos_status_router)

if UI_DIR.exists():
    app.mount("/ui", StaticFiles(directory=str(UI_DIR)), name="ui")

if FRONTEND_DIST_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST_DIR), html=True), name="frontend_dist")
elif FRONTEND_DIR.exists():
    app.mount("/frontend", StaticFiles(directory=str(FRONTEND_DIR)), name="frontend")
