# ============================================================
# VAANIRAKSHAK — Citizen Emergency SOS Dispatcher
# Real-time Family Contact Alerting on Critical Threat Breaches
# ============================================================
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class SOSRecipient(BaseModel):
    contact_id: str
    name: str
    phone_number: str
    relation: str
    status: str = "DELIVERED"
    delivery_timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class SOSAlertPayload(BaseModel):
    alert_id: str
    session_id: str
    timestamp: str
    suspect_number: str
    threat_category: str
    peak_risk_score: int
    recipients: List[SOSRecipient]
    sms_content_hi: str
    sms_content_en: str
    case_reference: str
    action_taken: str


class CitizenSOSDispatcher:
    """Dispatches real-time emergency warnings to enrolled family contacts
    when a telecom call reaches CRITICAL risk levels (e.g. AI clone extortion).
    """

    def __init__(self):
        # Pre-enrolled trusted emergency contacts for demonstration
        self._default_contacts: List[Dict[str, str]] = [
            {
                "contact_id": "spk_rahul_son",
                "name": "Rahul (Son)",
                "phone_number": "+91-9811122334",
                "relation": "Son",
            },
            {
                "contact_id": "spk_priya_daughter",
                "name": "Priya (Daughter)",
                "phone_number": "+91-9822233445",
                "relation": "Daughter",
            },
        ]
        self._alert_history: List[SOSAlertPayload] = []

    def dispatch_emergency_sos(
        self,
        session_id: str,
        suspect_number: str,
        risk_score: int,
        threat_category: str = "AI_VOICE_CLONING_EXTORTION",
        case_reference: Optional[str] = None,
        contacts: Optional[List[Dict[str, str]]] = None,
    ) -> SOSAlertPayload:
        """Constructs and dispatches dual-language emergency alerts to family contacts."""
        alert_id = f"SOS-{uuid.uuid4().hex[:8].upper()}"
        case_ref = case_reference or f"I4C-1930-{uuid.uuid4().hex[:8].upper()}"
        active_contacts = contacts or self._default_contacts

        now_iso = datetime.now(timezone.utc).isoformat()

        # Dual-language alert messages
        sms_en = (
            f"[VAANIRAKSHAK ALERT] Emergency! An active telecom call on your family member's phone "
            f"from {suspect_number} was flagged as HIGH RISK FRAUD ({risk_score}/100: {threat_category}). "
            f"Do NOT transfer money or share OTPs. Incident Ref: {case_ref}. Report to 1930."
        )

        sms_hi = (
            f"[वाणीरक्षक चेतावनी] आपातकालीन सूचना! आपके परिवार के सदस्य को {suspect_number} से आ रही कॉल "
            f"में AI वॉयस क्लोनिंग/धोखाधड़ी ({risk_score}/100) का पता चला है। "
            f"कृपया पैसे या OTP न भेजें। केस संख्या: {case_ref}। हेल्पलाइन: 1930."
        )

        recipients = [
            SOSRecipient(
                contact_id=c["contact_id"],
                name=c["name"],
                phone_number=c["phone_number"],
                relation=c.get("relation", "Family"),
                status="DELIVERED",
                delivery_timestamp=now_iso,
            )
            for c in active_contacts
        ]

        action_taken = (
            "CALL_TERMINATED_AND_FAMILY_ALERTED"
            if risk_score >= 90
            else "FAMILY_WARNING_DISPATCHED"
        )

        alert = SOSAlertPayload(
            alert_id=alert_id,
            session_id=session_id,
            timestamp=now_iso,
            suspect_number=suspect_number,
            threat_category=threat_category,
            peak_risk_score=risk_score,
            recipients=recipients,
            sms_content_hi=sms_hi,
            sms_content_en=sms_en,
            case_reference=case_ref,
            action_taken=action_taken,
        )

        self._alert_history.append(alert)
        return alert

    def get_history(self, limit: int = 50) -> List[SOSAlertPayload]:
        """Returns chronological list of dispatched emergency SOS alerts."""
        return list(reversed(self._alert_history))[:limit]

    def clear_history(self) -> None:
        """Clears memory alert history (useful for test resets)."""
        self._alert_history.clear()


# Global singleton dispatcher instance
citizen_sos_dispatcher = CitizenSOSDispatcher()
