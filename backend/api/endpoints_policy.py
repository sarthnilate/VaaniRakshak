"""
============================================================
VAANIRAKSHAK — Live Policy Configuration Endpoints
============================================================
Allows security operators and SIH evaluators to dynamically
tune threshold policies, intervention countdown windows, and defense modes.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any

from backend.config import settings

router = APIRouter(prefix="/policy", tags=["Dynamic Defense Policy Tuning"])

# Active runtime configuration state initialized from settings
_ACTIVE_POLICY: Dict[str, Any] = {
    "intervention_window_sec": settings.INTERVENTION_WINDOW_SEC,
    "critical_threshold": settings.RISK_THRESHOLD_CRITICAL,
    "high_threshold": settings.RISK_THRESHOLD_HIGH,
    "medium_threshold": settings.RISK_THRESHOLD_MEDIUM,
    "low_threshold": settings.RISK_THRESHOLD_LOW,
    "auto_block_enabled": True,
    "operational_tier": "TIER_2_RESEARCH_DEMO",
    "screening_unknown_numbers_only": True,
}


class PolicyUpdateRequest(BaseModel):
    intervention_window_sec: int = Field(default=10, ge=3, le=30, description="Intervention countdown window (seconds)")
    critical_threshold: int = Field(default=85, ge=70, le=98, description="Critical risk cutoff (0-100)")
    high_threshold: int = Field(default=65, ge=50, le=84, description="High risk cutoff (0-100)")
    medium_threshold: int = Field(default=35, ge=20, le=64, description="Medium risk cutoff (0-100)")
    low_threshold: int = Field(default=15, ge=5, le=34, description="Low risk cutoff (0-100)")
    auto_block_enabled: bool = Field(default=True, description="Enables automated intervention at 0s countdown")
    operational_tier: str = Field(default="TIER_2_RESEARCH_DEMO", description="TIER_1_CONSUMER | TIER_2_RESEARCH_DEMO | TIER_3_CARRIER")
    screening_unknown_numbers_only: bool = Field(default=True, description="Only screen calls from unverified/unknown numbers")


@router.get("", summary="Get Current Defense Policy Matrix")
async def get_active_policy():
    """Returns currently enforced risk thresholds and intervention parameters."""
    return {
        "status": "ACTIVE",
        "policy": _ACTIVE_POLICY,
    }


@router.post("/update", summary="Update Defense Policy in Real-Time")
async def update_policy(req: PolicyUpdateRequest):
    """
    Dynamically updates active defense policy thresholds without restarting backend.
    """
    if not (req.low_threshold < req.medium_threshold < req.high_threshold < req.critical_threshold):
        raise HTTPException(
            status_code=400,
            detail="Thresholds must satisfy ordering: low < medium < high < critical",
        )

    _ACTIVE_POLICY.update(req.model_dump())
    return {
        "status": "POLICY_UPDATED",
        "policy": _ACTIVE_POLICY,
    }


@router.post("/reset", summary="Reset Policy to SIH 2026 Baseline Defaults")
async def reset_policy():
    """Resets defense policy to standard hackathon baseline specifications."""
    _ACTIVE_POLICY.update({
        "intervention_window_sec": settings.INTERVENTION_WINDOW_SEC,
        "critical_threshold": settings.RISK_THRESHOLD_CRITICAL,
        "high_threshold": settings.RISK_THRESHOLD_HIGH,
        "medium_threshold": settings.RISK_THRESHOLD_MEDIUM,
        "low_threshold": settings.RISK_THRESHOLD_LOW,
        "auto_block_enabled": True,
        "operational_tier": "TIER_2_RESEARCH_DEMO",
        "screening_unknown_numbers_only": True,
    })
    return {
        "status": "RESET_TO_DEFAULTS",
        "policy": _ACTIVE_POLICY,
    }
