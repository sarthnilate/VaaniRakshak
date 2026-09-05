from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class GeneratorMetadata(BaseModel):
    """Metadata describing a synthetic voice generator family."""
    generator_id: str = Field(..., description="Unique generator identifier")
    name: str = Field(..., description="Display name of generator model")
    family: str = Field(..., description="Model family e.g. Bark, Coqui-XTTS, OpenVoice")
    version: str = Field(..., description="Model version code")
    supported_languages: List[str] = Field(default_factory=list)


class ValidationResult(BaseModel):
    """Result returned when validating reference speaker audio for cloning."""
    is_valid: bool = Field(..., description="True if sample meets consent and audio quality criteria")
    reason: str = Field(..., description="Validation summary or error explanation")
    noise_floor_db: float = Field(default=-45.0, description="Measured background noise floor in dB")


class SyntheticAudioResult(BaseModel):
    """Payload containing generated synthetic audio and provenance metadata."""
    sample_id: str = Field(..., description="Unique sample identifier")
    pcm_b64: str = Field(..., description="Base64 encoded 16kHz PCM audio chunk")
    prompt: str = Field(..., description="Text prompt used for voice generation")
    language: str = Field(..., description="Target language code")
    generator_family: str = Field(..., description="Generator family code")
    reference_speaker_id: str = Field(..., description="Consented reference speaker ID")
    provenance_metadata: Dict[str, Any] = Field(default_factory=dict, description="Cryptographic provenance payload")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class VoiceGenerator(ABC):
    """Abstract base class for all Attack Lab voice cloning generator adapters."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        reference_speaker_id: str,
        language: str = "en",
        consent_token: Optional[str] = None
    ) -> SyntheticAudioResult:
        """Generates synthetic audio given prompt and reference speaker profile."""
        pass

    @abstractmethod
    def validate_reference(self, reference_audio_path: str) -> ValidationResult:
        """Validates sample length, noise floor, and speaker consent metadata."""
        pass

    @abstractmethod
    def supported_languages(self) -> List[str]:
        """Returns ISO language codes supported by this generator adapter."""
        pass

    @abstractmethod
    def metadata(self) -> GeneratorMetadata:
        """Returns generator family, model version, and capability profile."""
        pass
