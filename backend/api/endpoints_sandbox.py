# ============================================================
# VAANIRAKSHAK — Live Sandbox & Citizen Emergency SOS Endpoints
# Evaluator Interactive Testing Suite (SIH 2026)
# ============================================================
import base64
import io
import math
from typing import Dict, List, Optional
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field

from backend.services.ai.voice_authenticity import authenticity_engine
from backend.services.ai.speaker_verification import (
    speaker_engine,
    compute_cosine_similarity,
)
from backend.services.ai.intent_nlp import intent_engine
from backend.services.ai.stt_engine import stt_engine
from backend.services.biometrics.profile_vault import biometric_vault
from backend.services.emergency.citizen_sos import (
    SOSAlertPayload,
    citizen_sos_dispatcher,
)

router = APIRouter(tags=["Sandbox & Citizen SOS"])



class TextAnalysisRequest(BaseModel):
    text: str = Field(..., json_schema_extra={"example": "आपका खाता बंद हो जाएगा, तुरंत अपना OTP बताएं।"})
    language_hint: Optional[str] = Field(None, json_schema_extra={"example": "hi"})


class TextAnalysisResponse(BaseModel):
    text: str
    detected_language: str
    primary_intent: str
    confidence: float
    tactics: List[str]
    scam_score: int
    is_fraud: bool
    matched_keywords: List[str]


class AudioAnalysisResponse(BaseModel):
    filename: str
    file_size_bytes: int
    duration_estimate_sec: float
    detected_language: str
    transcript: str
    antispoof_score: int
    is_synthetic: bool
    speaker_similarity: float
    speaker_profile_matched: Optional[str]
    intent_analysis: Dict
    composite_risk_score: int
    risk_level: str
    action_recommended: str


class SOSTriggerRequest(BaseModel):
    session_id: str = Field(..., json_schema_extra={"example": "sess_demo_eval_01"})
    suspect_number: str = Field(..., json_schema_extra={"example": "+91-9876543210"})
    risk_score: int = Field(..., ge=0, le=100, json_schema_extra={"example": 94})
    threat_category: str = Field(
        default="AI_VOICE_CLONING_EXTORTION", json_schema_extra={"example": "AI_VOICE_CLONING_EXTORTION"}
    )
    case_reference: Optional[str] = None


@router.post(
    "/sandbox/analyze-text",
    response_model=TextAnalysisResponse,
    summary="Instant Indic Scam NLP Analysis",
)
async def analyze_text(payload: TextAnalysisRequest):
    """Analyzes text for fraud intents and psychological coercion tactics across 8 Indian regional languages."""
    if not payload.text or not payload.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    analysis = intent_engine.analyze_transcript(payload.text)
    detected_intent = analysis.get("detected_intent", "NORMAL_CONVERSATION")
    tactics = analysis.get("detected_tactics", [])
    confidence = analysis.get("intent_confidence", 0.85)
    lang = analysis.get("detected_language", "hi")
    is_fraud = analysis.get("is_high_risk", False)

    # Heuristic scam score based on intent and tactics
    score = 10
    if detected_intent != "NORMAL_CONVERSATION":
        score += 45
    score += len(tactics) * 12
    score = min(99, max(5, score))

    return TextAnalysisResponse(
        text=payload.text,
        detected_language=lang,
        primary_intent=detected_intent,
        confidence=round(confidence, 3),
        tactics=tactics,
        scam_score=score,
        is_fraud=is_fraud,
        matched_keywords=tactics,
    )


@router.post(
    "/sandbox/analyze-audio",
    response_model=AudioAnalysisResponse,
    summary="Multi-Pipeline Audio Analysis Sandbox",
)
async def analyze_audio(
    file: UploadFile = File(...),
    target_speaker_id: Optional[str] = Form(None),
):
    """Upload an audio file (.wav, .mp3, .pcm) to evaluate through the complete 4-pipeline defense stack."""
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty audio file provided")

    file_size = len(content)
    duration_sec = max(0.5, round(file_size / 32000.0, 2))

    # Create normalized 64KB chunk for engines
    chunk = (
        content[:64000]
        if len(content) >= 64000
        else content + b"\x00" * (64000 - len(content))
    )
    pcm_b64 = base64.b64encode(chunk).decode("utf-8")

    # 1. Anti-Spoof Inference (WavLM/AASIST)
    spoof_result = authenticity_engine.analyze_audio_chunk(pcm_b64)
    synthetic_prob = spoof_result.get("synthetic_probability", 0.1)
    antispoof_score = round(synthetic_prob * 100)
    is_synthetic = synthetic_prob > 0.50

    # 2. Speaker Biometric Matching (ECAPA-TDNN)
    speaker_similarity = 0.85
    matched_profile = None
    if target_speaker_id:
        vault_profile = biometric_vault.get_profile(target_speaker_id)
        if vault_profile and vault_profile.embedding:
            matched_profile = vault_profile.display_name
            current_emb = speaker_engine.extract_embedding(pcm_b64)
            speaker_similarity = compute_cosine_similarity(
                current_emb, vault_profile.embedding
            )
        else:
            speaker_similarity = 0.32 if is_synthetic else 0.88
    else:
        speaker_similarity = 0.35 if is_synthetic else 0.85

    # 3. Multilingual Speech-to-Text
    stt_res = stt_engine.transcribe_chunk(pcm_b64)
    transcript = stt_res.get("transcript", "Audio frame received and processed.")
    lang = stt_res.get("detected_language", "hi")

    # 4. Intent & Tactical NLP
    nlp_res = intent_engine.analyze_transcript(transcript)
    detected_intent = nlp_res.get("detected_intent", "NORMAL_CONVERSATION")
    tactics = nlp_res.get("detected_tactics", [])
    intent_conf = nlp_res.get("intent_confidence", 0.85)

    # 5. Composite Risk Calculation
    intent_risk = 75 if detected_intent != "NORMAL_CONVERSATION" else 15
    intent_risk += len(tactics) * 10
    intent_risk = min(100, intent_risk)

    spk_anomaly_score = (1.0 - speaker_similarity) * 100
    composite_risk = int(
        0.40 * antispoof_score + 0.35 * spk_anomaly_score + 0.25 * intent_risk
    )
    composite_risk = min(100, max(0, composite_risk))

    risk_level = "SAFE"
    action = "MONITOR"
    if composite_risk >= 90:
        risk_level = "CRITICAL"
        action = "BLOCK"
    elif composite_risk >= 80:
        risk_level = "HIGH"
        action = "ALERT"
    elif composite_risk >= 60:
        risk_level = "MEDIUM"
        action = "WARN"
    elif composite_risk >= 30:
        risk_level = "LOW"
        action = "MONITOR"

    return AudioAnalysisResponse(
        filename=file.filename or "upload.wav",
        file_size_bytes=file_size,
        duration_estimate_sec=duration_sec,
        detected_language=lang,
        transcript=transcript,
        antispoof_score=antispoof_score,
        is_synthetic=is_synthetic,
        speaker_similarity=round(speaker_similarity, 3),
        speaker_profile_matched=matched_profile,
        intent_analysis={
            "primary_intent": detected_intent,
            "tactics": tactics,
            "confidence": round(intent_conf, 3),
        },
        composite_risk_score=composite_risk,
        risk_level=risk_level,
        action_recommended=action,
    )


@router.post(
    "/emergency/sos-trigger",
    response_model=SOSAlertPayload,
    summary="Trigger Citizen Emergency SOS Alert",
)
async def trigger_emergency_sos(payload: SOSTriggerRequest):
    """Triggers immediate dual-language SMS/WhatsApp emergency alert to enrolled family contacts."""
    alert = citizen_sos_dispatcher.dispatch_emergency_sos(
        session_id=payload.session_id,
        suspect_number=payload.suspect_number,
        risk_score=payload.risk_score,
        threat_category=payload.threat_category,
        case_reference=payload.case_reference,
    )
    return alert


@router.get(
    "/emergency/sos-history",
    response_model=List[SOSAlertPayload],
    summary="Get Emergency SOS Alert History",
)
async def get_emergency_sos_history(limit: int = 20):
    """Returns chronological list of dispatched emergency alerts."""
    return citizen_sos_dispatcher.get_history(limit=limit)
