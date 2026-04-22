from __future__ import annotations

import os
from fastapi import Request
from fastapi.responses import JSONResponse

PUBLIC_PATHS = {
    "/health", "/ping",
    "/db/ping", "/postgres/ping",
    "/docs", "/openapi.json", "/redoc",
    "/version", "/auth/verify"
}

def _get_key(request: Request):
    auth = request.headers.get("authorization", "")
    return (
        request.headers.get("x-api-key")
        or (auth.replace("Bearer ", "") if auth.startswith("Bearer ") else None)
    )

def install_auth(app):
    @app.middleware("http")
    async def auth(request: Request, call_next):
        path = request.url.path

        if path in PUBLIC_PATHS:
            return await call_next(request)

        key = os.getenv("PROMETEO_API_KEY")

        if not key:
            return await call_next(request)

        if _get_key(request) != key:
            return JSONResponse({"detail": "unauthorized"}, status_code=401)

        return await call_next(request)
