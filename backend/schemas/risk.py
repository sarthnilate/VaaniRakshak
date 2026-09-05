from typing import List, Optional
from pydantic import BaseModel, Field


class EvidenceItem(BaseModel):
    """Individual structured evidence vector."""
    type: str = Field(..., description="Evidence type (e.g. synthetic_voice, speaker_similarity, money_request, urgency)")
    score: float = Field(..., ge=0.0, le=1.0, description="Normalized evidence score between 0.0 and 1.0")
    details: Optional[str] = Field(default=None, description="Human readable evidence context")


class EvidenceSummary(BaseModel):
    """Aggregated evidence summary snapshot for real-time inspection."""
    synthetic_probability: float = Field(default=0.0, ge=0.0, le=1.0)
    human_probability: float = Field(default=1.0, ge=0.0, le=1.0)
    speaker_similarity: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    detected_intent: str = Field(default="NORMAL_CONVERSATION")
    detected_tactics: List[str] = Field(default_factory=list)
    transcript_snippet: str = Field(default="")


class RiskUpdatePayload(BaseModel):
    """Real-time risk update packet broadcasted to Android client and Command Center."""
    type: str = Field(default="risk_update", description="Message type tag")
    session_id: str = Field(..., description="Call session UUID")
    sequence: int = Field(..., ge=0, description="Chunk sequence index")
    timestamp_ms: int = Field(default=0, ge=0)
    risk_score: int = Field(..., ge=0, le=100, description="Dynamic aggregate risk score (0 - 100)")
    band: str = Field(..., description="Risk band: SAFE, LOW, MEDIUM, HIGH, CRITICAL")
    action: str = Field(..., description="Recommended action: MONITOR, ALERT_USER, INTERVENE_RECOMMENDED")
    evidence_summary: EvidenceSummary = Field(..., description="High-level evidence metrics")
    evidence: List[EvidenceItem] = Field(default_factory=list, description="Structured evidence list")
    policy_window_sec: int = Field(default=10, description="Configurable policy intervention window")
