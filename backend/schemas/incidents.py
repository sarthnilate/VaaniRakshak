from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from backend.schemas.risk import EvidenceSummary, EvidenceItem


class IncidentPayload(BaseModel):
    """Payload representing a logged threat incident."""
    incident_id: str = Field(..., description="Unique incident ID")
    session_id: str = Field(..., description="Associated call session ID")
    caller_phone: str = Field(..., description="Masked/Hashed caller phone number")
    peak_risk_score: int = Field(..., ge=0, le=100)
    risk_band: str = Field(..., description="SAFE, LOW, MEDIUM, HIGH, CRITICAL")
    evidence_summary: EvidenceSummary
    evidence_items: List[EvidenceItem] = Field(default_factory=list)
    action_taken: str = Field(..., description="TERMINATED, USER_DISMISSED, IGNORED")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SpeakerProfilePayload(BaseModel):
    """Payload for enrolling a consented speaker biometric profile."""
    display_name: str = Field(..., min_length=2, description="Trusted contact display name")
    phone_number: str = Field(..., min_length=3, description="Contact phone number")
    consent_given: bool = Field(..., description="Explicit user consent flag")
    embedding: List[float] = Field(..., min_length=1, description="192-dimensional ECAPA-TDNN embedding vector")

    @field_validator('consent_given')
    @classmethod
    def validate_consent(cls, v: bool) -> bool:
        if not v:
            raise ValueError("Explicit user consent is mandatory for speaker profile enrollment.")
        return v



class SpeakerProfileResponse(BaseModel):
    """Public response for enrolled speaker profile."""
    speaker_id: str
    display_name: str
    phone_number: str
    consent_given: bool
    created_at: datetime
