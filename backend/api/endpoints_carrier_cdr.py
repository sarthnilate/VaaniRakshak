"""
============================================================
VAANIRAKSHAK — Carrier CDR Extended Endpoints (Phase 14)
============================================================
Adds path-parameter-based SIP 603 teardown:
  POST /api/v1/carrier/teardown/{session_id}

The main CDR and fraud-hotspot endpoints are served by the
existing carrier_router in endpoints_forensics.py (mounted first
under /api/v1/carrier/) which has been augmented with Phase 14
fraud_hotspot_active, sip_circuit_state, sip_teardown_dispatched fields.
"""
from fastapi import APIRouter
from typing import Any, Dict
from backend.services.carrier.sip_trunk_adapter import carrier_adapter

router = APIRouter(prefix="/carrier", tags=["Carrier CDR & Telecom"])


@router.post("/teardown/{session_id}", summary="Dispatch SIP 603 Teardown by session ID (path param)")
async def dispatch_teardown_by_id(session_id: str) -> Dict[str, Any]:
    """
    Triggers automated SIP BYE (603 Decline) to immediately terminate
    a carrier telecom circuit flagged as fraudulent by the VaaniRakshak AI engine.
    Uses session_id as a path parameter (no request body required).
    """
    result = carrier_adapter.trigger_carrier_teardown(
        session_id,
        reason="VAANIRAKSHAK_AI_FRAUD_CONFIRMED_PHASE14"
    )
    return {
        "call_id": result.call_id,
        "status": result.status,
        "sip_response_code": result.sip_response_code,
        "teardown_timestamp": result.teardown_timestamp,
        "reason": result.reason,
        "message": (
            "SIP 603 Decline dispatched. Carrier circuit will terminate within 2 seconds."
            if result.sip_response_code == 603
            else "Circuit not found or already terminated."
        ),
    }
