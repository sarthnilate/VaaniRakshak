from fastapi import APIRouter
from backend.config import settings
from backend.api.endpoints_session import router as session_router
from backend.api.endpoints_incidents import router as incident_router
from backend.api.endpoints_speakers import router as speaker_router
from backend.api.endpoints_attack_lab import router as attack_lab_router
from backend.api.endpoints_forensics import (
    router as forensics_router,
    carrier_router,
)
from backend.api.endpoints_policy import router as policy_router
from backend.api.endpoints_sandbox import router as sandbox_router
from backend.api.endpoints_carrier_cdr import router as carrier_cdr_router
from backend.api.endpoints_telemetry import router as telemetry_router
from backend.api.endpoints_admin import router as admin_router

api_router = APIRouter(prefix=settings.API_V1_PREFIX)


@api_router.get("/health", tags=["Health"])
async def health_check():
    """System health check endpoint."""
    return {
        "status": "HEALTHY",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "policy": {
            "intervention_window_sec": settings.INTERVENTION_WINDOW_SEC,
            "critical_threshold": settings.RISK_THRESHOLD_CRITICAL,
            "high_threshold": settings.RISK_THRESHOLD_HIGH,
            "medium_threshold": settings.RISK_THRESHOLD_MEDIUM,
            "low_threshold": settings.RISK_THRESHOLD_LOW
        }
    }


api_router.include_router(session_router)
api_router.include_router(incident_router)
api_router.include_router(speaker_router)
api_router.include_router(attack_lab_router)
api_router.include_router(forensics_router)
api_router.include_router(carrier_router)
api_router.include_router(policy_router)
api_router.include_router(sandbox_router)
api_router.include_router(carrier_cdr_router)
api_router.include_router(telemetry_router)
api_router.include_router(admin_router)


