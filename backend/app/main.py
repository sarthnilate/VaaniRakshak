"""
VaaniRakshak backend gateway entrypoint.

Phase 0 scope: a booting FastAPI application with health checks and clean
module boundaries (api / auth / calls / websocket / risk / incidents /
settings) ready to be filled in by later phases per Phases.md. No ML,
no call sessions, no WebSocket streaming yet - those are Phase 3+ and
Phase 11.
"""

from fastapi import FastAPI

from app.api.router import api_router
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.0.1-phase0",
    debug=settings.debug,
)

app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/")
async def root() -> dict:
    return {
        "service": settings.app_name,
        "status": "ok",
        "docs": "/docs",
        "health": f"{settings.api_v1_prefix}/health",
    }
