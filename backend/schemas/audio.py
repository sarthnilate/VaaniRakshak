from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class AudioChunkPayload(BaseModel):
    """Payload representing a single audio PCM chunk sent via WebSocket."""
    type: str = Field(default="audio_chunk", description="Message type tag")
    sequence: int = Field(..., ge=0, description="Chunk sequence index")
    timestamp_ms: int = Field(..., ge=0, description="Timestamp in milliseconds from start of call")
    pcm_b64: str = Field(..., min_length=1, description="Base64 encoded 16kHz 16-bit mono PCM audio data")
    sample_rate: int = Field(default=16000, description="Sample rate in Hz")
    channels: int = Field(default=1, description="Number of audio channels")


class SessionInitPayload(BaseModel):
    """Payload to initialize a protected call session."""
    caller_phone: str = Field(..., min_length=3, description="Incoming caller phone number")
    is_unknown_caller: bool = Field(default=True, description="True if caller is not in user contacts")
    protected_contact_id: Optional[str] = Field(default=None, description="Enrolled trusted contact ID if matched")
    language: str = Field(default="en", description="Preferred language ISO code")
    sample_rate: int = Field(default=16000, description="Audio sample rate")


class SessionInitResponse(BaseModel):
    """Response returned upon call session initialization."""
    session_id: str = Field(..., description="Unique call session UUID")
    status: str = Field(default="ACTIVE", description="Session state (ACTIVE, TERMINATED, COMPLETED)")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    intervention_window_sec: int = Field(..., description="Configured intervention window seconds")
    critical_threshold: int = Field(..., description="Critical risk score threshold")
