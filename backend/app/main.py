from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router as api_router
from app.db.session import init_db

app = FastAPI(title="PROMETEO API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    try:
        init_db()
        print("DB INIT OK")
    except Exception as e:
        print("DB INIT ERROR:", str(e))

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(api_router)
