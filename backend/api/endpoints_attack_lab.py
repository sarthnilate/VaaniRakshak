from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from backend.attack_lab.base_generator import GeneratorMetadata, SyntheticAudioResult
from backend.attack_lab.adapters.mock_adapter import MockResearchAdapter
from backend.attack_lab.adapters.bark_coqui_adapter import BarkCoquiAdapter
from backend.attack_lab.adapters.openvoice_adapter import OpenVoiceAdapter
from backend.attack_lab.degradation import degradation_simulator
from backend.services.session_service import session_service

router = APIRouter(prefix="/attack_lab", tags=["System A: Attack Lab"])

# Registry of active generator adapters
GENERATOR_REGISTRY = {
    "mock": MockResearchAdapter(),
    "bark_coqui": BarkCoquiAdapter(),
    "openvoice": OpenVoiceAdapter()
}


class GenerateRequestPayload(BaseModel):
    """Payload to request synthetic attack sample generation."""
    generator_key: str = Field(default="mock", description="Registered generator key (mock, bark_coqui, openvoice)")
    prompt: str = Field(..., min_length=2, description="Text script to synthesize")
    reference_speaker_id: str = Field(..., description="Consented reference speaker ID")
    language: str = Field(default="en", description="Target language ISO code")
    consent_token: Optional[str] = Field(default="CONSENT_RESEARCH_APPROVED", description="Explicit research consent token")
    apply_degradation: bool = Field(default=False, description="True to pass audio through cellular degradation simulator")
    codec: str = Field(default="AMR-WB", description="Cellular codec e.g. AMR-WB, AMR-NB")
    snr_db: float = Field(default=15.0, description="Signal-to-noise ratio in dB")


class SimulateAttackPayload(BaseModel):
    """Payload to trigger end-to-end attack simulation against a live session."""
    session_id: str = Field(..., description="Target active call session UUID")
    generator_key: str = Field(default="mock")
    prompt: str = Field(..., description="Malicious script e.g. 'I need your help urgently. Send ₹20,000 to this UPI ID.'")
    reference_speaker_id: str = Field(..., description="Consented target reference speaker ID")
    simulated_synthetic_prob: float = Field(default=0.96, ge=0.0, le=1.0)
    simulated_speaker_sim: float = Field(default=0.92, ge=0.0, le=1.0)


@router.get("/generators", response_model=List[GeneratorMetadata])
async def list_generators():
    """Lists all available synthetic voice generator adapters registered in System A Attack Lab."""
    return [adapter.metadata() for adapter in GENERATOR_REGISTRY.values()]


@router.post("/generate", response_model=SyntheticAudioResult, status_code=status.HTTP_201_CREATED)
async def generate_synthetic_audio(payload: GenerateRequestPayload):
    """Generates synthetic audio sample with cryptographic provenance metadata."""
    if payload.generator_key not in GENERATOR_REGISTRY:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown generator key '{payload.generator_key}'. Available keys: {list(GENERATOR_REGISTRY.keys())}"
        )

    adapter = GENERATOR_REGISTRY[payload.generator_key]
    result = await adapter.generate(
        prompt=payload.prompt,
        reference_speaker_id=payload.reference_speaker_id,
        language=payload.language,
        consent_token=payload.consent_token
    )

    if payload.apply_degradation:
        degraded_pcm = degradation_simulator.degrade_audio_chunk(
            pcm_b64=result.pcm_b64,
            codec=payload.codec,
            snr_db=payload.snr_db
        )
        result.pcm_b64 = degraded_pcm
        result.provenance_metadata["degradation_applied"] = {
            "codec": payload.codec,
            "snr_db": payload.snr_db
        }

    return result


@router.post("/simulate_attack")
async def simulate_attack_on_session(payload: SimulateAttackPayload):
    """Injects a controlled synthetic attack sample into a live defense call session."""
    if payload.generator_key not in GENERATOR_REGISTRY:
        raise HTTPException(status_code=400, detail="Invalid generator key")

    adapter = GENERATOR_REGISTRY[payload.generator_key]
    synth_res = await adapter.generate(
        prompt=payload.prompt,
        reference_speaker_id=payload.reference_speaker_id
    )

    simulated_vector = {
        "synthetic_prob": payload.simulated_synthetic_prob,
        "speaker_sim": payload.simulated_speaker_sim,
        "intent": "MONEY_TRANSFER" if "money" in payload.prompt.lower() or "₹" in payload.prompt or "20,000" in payload.prompt or "upi" in payload.prompt.lower() else "OTP_REQUEST",
        "tactics": ["URGENCY", "PRESSURE"],
        "transcript": payload.prompt,
        "risk_score": 94 if payload.simulated_synthetic_prob > 0.9 else 65
    }

    risk_update = await session_service.update_session_risk(
        session_id=payload.session_id,
        sequence=1,
        timestamp_ms=1000,
        pcm_b64=synth_res.pcm_b64,
        raw_evidence_vector=simulated_vector
    )

    return {
        "status": "ATTACK_SIMULATED",
        "sample_id": synth_res.sample_id,
        "provenance": synth_res.provenance_metadata,
        "defense_response": risk_update.model_dump(mode="json")
    }
