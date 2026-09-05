import pytest
from pydantic import ValidationError
from backend.schemas.audio import AudioChunkPayload, SessionInitPayload
from backend.schemas.risk import RiskUpdatePayload, EvidenceSummary, EvidenceItem
from backend.schemas.incidents import SpeakerProfilePayload


def test_audio_chunk_payload_valid():
    payload = AudioChunkPayload(
        sequence=1,
        timestamp_ms=1000,
        pcm_b64="c2FtcGxlcGNtZGF0YQ=="
    )
    assert payload.type == "audio_chunk"
    assert payload.sequence == 1
    assert payload.sample_rate == 16000


def test_audio_chunk_payload_invalid():
    with pytest.raises(ValidationError):
        AudioChunkPayload(sequence=-1, timestamp_ms=0, pcm_b64="")


def test_session_init_payload():
    payload = SessionInitPayload(
        caller_phone="+919876543210",
        is_unknown_caller=True,
        language="hi"
    )
    assert payload.caller_phone == "+919876543210"
    assert payload.is_unknown_caller is True
    assert payload.language == "hi"


def test_risk_update_payload():
    summary = EvidenceSummary(
        synthetic_probability=0.96,
        human_probability=0.04,
        speaker_similarity=0.92,
        detected_intent="MONEY_TRANSFER",
        detected_tactics=["URGENCY"]
    )
    evidence = [
        EvidenceItem(type="synthetic_voice", score=0.96, details="High synthetic probability"),
        EvidenceItem(type="speaker_impersonation", score=0.92, details="High speaker similarity")
    ]
    payload = RiskUpdatePayload(
        session_id="sess_12345",
        sequence=5,
        timestamp_ms=5000,
        risk_score=94,
        band="CRITICAL",
        action="INTERVENE_RECOMMENDED",
        evidence_summary=summary,
        evidence=evidence,
        policy_window_sec=10
    )

    assert payload.risk_score == 94
    assert payload.band == "CRITICAL"
    assert payload.action == "INTERVENE_RECOMMENDED"
    assert payload.policy_window_sec == 10
    assert len(payload.evidence) == 2


def test_speaker_profile_payload_consent_required():
    with pytest.raises(ValidationError):
        SpeakerProfilePayload(
            display_name="Trusted Contact",
            phone_number="+919876543210",
            consent_given=False,
            embedding=[0.1] * 192
        )

