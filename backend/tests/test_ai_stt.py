import pytest
from backend.services.ai.stt_engine import stt_engine, SUPPORTED_LANGUAGES


def test_stt_languages_supported():
    assert "hi" in SUPPORTED_LANGUAGES
    assert "mr" in SUPPORTED_LANGUAGES
    assert "en" in SUPPORTED_LANGUAGES
    assert len(SUPPORTED_LANGUAGES) >= 16


def test_stt_transcribe_override():
    simulated = {"transcript": "I need your help urgently. Send ₹20,000 to this UPI ID right now.", "language": "en"}
    res = stt_engine.transcribe_chunk(pcm_b64="dummy", simulated_override=simulated)
    assert res["transcription"] == "I need your help urgently. Send ₹20,000 to this UPI ID right now."
    assert res["detected_language"] == "en"
