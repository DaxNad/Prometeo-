from importlib import import_module
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles

BASE_DIR = Path(__file__).resolve().parent.parent
UI_DIR = BASE_DIR / "ui"
FRONTEND_DIR = BASE_DIR.parent / "frontend"
FRONTEND_DIST_DIR = FRONTEND_DIR / "dist"

app = FastAPI(
    title="PROMETEO CORE DIAGNOSTIC",
    version="diag-1",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import_results: dict[str, dict] = {}

ROUTERS = [
    ("app.api.devos", "router", "devos"),
    ("app.api.devos_status", "router", "devos_status"),
    ("app.api.events", "router", "events"),
    ("app.api.postgres_probe", "router", "postgres_probe"),
    ("app.api.production_events", "router", "production_events"),
    ("app.api.state", "router", "state"),
    ("app.api_search", "router", "search"),
    ("app.api_smf", "router", "smf"),
    ("app.api_production", "router", "production"),
    ("app.api_dashboard", "router", "dashboard"),
]

for module_name, attr_name, label in ROUTERS:
    try:
        module = import_module(module_name)
        router = getattr(module, attr_name)
        app.include_router(router)
        import_results[label] = {
            "ok": True,
            "module": module_name,
            "error": None,
        }
        print(f"IMPORT OK: {label} -> {module_name}")
    except Exception as e:
        import_results[label] = {
            "ok": False,
            "module": module_name,
            "error": str(e),
        }
        print(f"IMPORT ERROR: {label} -> {module_name} -> {e}")


@app.get("/")
def root():
    dist_index = FRONTEND_DIST_DIR / "index.html"
    if dist_index.exists():
        return FileResponse(dist_index)

    ui_index = UI_DIR / "index.html"
    if ui_index.exists():
        return FileResponse(ui_index)

    return {
        "service": "PROMETEO CORE DIAGNOSTIC",
        "version": "diag-1",
    }


@app.get("/health")
def health():
    return {
        "ok": True,
        "service": "PROMETEO CORE DIAGNOSTIC",
        "version": "diag-1",
        "ui_available": UI_DIR.exists() or FRONTEND_DIST_DIR.exists(),
        "imports": import_results,
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


if UI_DIR.exists():
    app.mount("/ui", StaticFiles(directory=str(UI_DIR)), name="ui")

if FRONTEND_DIST_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST_DIR), html=True), name="frontend_dist")
elif FRONTEND_DIR.exists():
    app.mount("/frontend", StaticFiles(directory=str(FRONTEND_DIR)), name="frontend")
