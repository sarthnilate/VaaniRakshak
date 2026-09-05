"""
============================================================
VAANIRAKSHAK — Carrier Telephony Adapter Package
============================================================
"""
from backend.services.carrier.sip_trunk_adapter import (
    CarrierSipTrunkAdapter,
    CarrierCallEvent,
    CarrierTeardownResult,
)

__all__ = [
    "CarrierSipTrunkAdapter",
    "CarrierCallEvent",
    "CarrierTeardownResult",
]
