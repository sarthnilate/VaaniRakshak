"""
Top-level API router. Individual domain routers (calls, incidents, settings,
auth) are mounted here as they are implemented phase-by-phase; Phase 0 only
wires health.
"""

from fastapi import APIRouter

from app.api.health import router as health_router

api_router = APIRouter()
api_router.include_router(health_router)
