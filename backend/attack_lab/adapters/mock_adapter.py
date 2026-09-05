import uuid
import base64
import numpy as np
from typing import List, Optional

from backend.attack_lab.base_generator import (
    VoiceGenerator,
    SyntheticAudioResult,
    ValidationResult,
    GeneratorMetadata
)
from backend.attack_lab.provenance import provenance_tracker


class MockResearchAdapter(VoiceGenerator):
    """Fast offline research generator adapter for automated pipeline testing."""

    def __init__(self):
        self._metadata = GeneratorMetadata(
            generator_id="mock_research_v1",
            name="Mock Offline Research Generator",
            family="MockResearch",
            version="1.0.0",
            supported_languages=["en", "hi", "mr", "bn", "ta", "te", "gu", "pa"]
        )

    def metadata(self) -> GeneratorMetadata:
        return self._metadata

    def supported_languages(self) -> List[str]:
        return self._metadata.supported_languages

    def validate_reference(self, reference_audio_path: str) -> ValidationResult:
        return ValidationResult(
            is_valid=True,
            reason="Mock reference validated successfully.",
            noise_floor_db=-48.5
        )

    async def generate(
        self,
        prompt: str,
        reference_speaker_id: str,
        language: str = "en",
        consent_token: Optional[str] = "CONSENT_RESEARCH_APPROVED"
    ) -> SyntheticAudioResult:
        sample_id = f"synth_{uuid.uuid4().hex[:10]}"

        # Generate 1 second of 16kHz sine wave audio chunk with subtle phase noise
        t = np.linspace(0, 1.0, 16000, False)
        sine_wave = 0.5 * np.sin(2 * np.pi * 440 * t) + 0.1 * np.random.normal(0, 1, 16000)
        int16_array = (sine_wave * 32767.0).astype(np.int16)
        pcm_b64 = base64.b64encode(int16_array.tobytes()).decode("utf-8")

        # Create cryptographic provenance payload
        provenance = provenance_tracker.create_provenance(
            sample_id=sample_id,
            generator_family=self._metadata.family,
            prompt=prompt,
            reference_speaker_id=reference_speaker_id,
            consent_token=consent_token or "CONSENT_RESEARCH_APPROVED"
        )

        return SyntheticAudioResult(
            sample_id=sample_id,
            pcm_b64=pcm_b64,
            prompt=prompt,
            language=language,
            generator_family=self._metadata.family,
            reference_speaker_id=reference_speaker_id,
            provenance_metadata=provenance
        )
