from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles

from .api.devos import router as dev_router
from .api.events import router as events_router
from .api.state import router as state_router
from .api_search import router as search_router
from .config import settings
from .db import init_db

BASE_DIR = Path(__file__).resolve().parent.parent
UI_DIR = BASE_DIR / "ui"
FRONTEND_DIR = BASE_DIR.parent / "frontend"

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


@app.on_event("startup")
def startup_event() -> None:
    init_db()


@app.get("/")
def root():
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {
        "service": settings.service_name,
        "version": settings.version,
    }


@app.get("/health")
def health():
    return {
        "ok": True,
        "service": settings.service_name,
        "version": settings.version,
        "ui_available": settings.ui_available,
        "database_configured": True,
    }


@app.get("/ping")
def ping():
    return {"status": "ok"}


@app.head("/ping")
def ping_head():
    return Response(status_code=200)


@app.get("/mobile")
def mobile():
    mobile_file = FRONTEND_DIR / "mobile.html"
    if mobile_file.exists():
        return FileResponse(mobile_file)
    return Response(status_code=404)


app.include_router(dev_router)
app.include_router(search_router)
app.include_router(events_router)
app.include_router(state_router)

if UI_DIR.exists():
    app.mount("/ui", StaticFiles(directory=str(UI_DIR)), name="ui")

if FRONTEND_DIR.exists():
    app.mount("/frontend", StaticFiles(directory=str(FRONTEND_DIR)), name="frontend")
