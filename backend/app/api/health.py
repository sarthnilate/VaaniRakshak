"""
Health check endpoints.

Phase 0 acceptance requires every service to expose a health check
(README/Phases.md). This module reports gateway liveness plus the
reachability of its direct dependencies (Redis, Postgres) without ever
blocking startup on them - a dependency being down is reported, not fatal.
"""

from fastapi import APIRouter

from db.session import ping_database
from services.redis_client import ping_redis

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict:
    """Liveness probe: process is up. Always returns 200 if reachable."""
    return {"status": "ok", "service": "vaanirakshak-gateway"}


@router.get("/health/ready")
async def readiness() -> dict:
    """Readiness probe: reports dependency connectivity for observability."""
    redis_ok = await ping_redis()
    db_ok = await ping_database()
    overall = "ok" if (redis_ok and db_ok) else "degraded"
    return {
        "status": overall,
        "dependencies": {
            "redis": "ok" if redis_ok else "unreachable",
            "database": "ok" if db_ok else "unreachable",
        },
    }
