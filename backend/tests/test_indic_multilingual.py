"""
============================================================
Phase 11 — Indic Multilingual NLP & Telephony Loopback Tests
============================================================
Verifies:
  - Indic language detection across 7 regional Indian languages (MR, TA, TE, BN, GU, PA, HI)
  - Multilingual intent extraction (OTP, Money Transfer, Bank, Threat, Emergency)
  - Multilingual tactic classification (Urgency, Fear, Authority, Secrecy, Pressure)
  - Telephony loopback PCM audio chunk generation (16kHz 16-bit mono)
  - Scenario profile generation (SIH 1-3 and Indic Marathi/Tamil)
"""
import pytest
from backend.services.ai.intent_nlp import (
    intent_engine,
    detect_indic_language,
)
from backend.services.telephony.loopback_streamer import (
    LiveLoopbackAudioStreamer,
    stream_scenario_loopback,
    SCENARIO_PROFILES,
)
from backend.services.ai.pipeline_aggregator import MultiEvidencePipeline


class TestIndicLanguageDetection:
    """Verifies heuristic language identification across Indian scripts."""

    def test_detect_hindi(self):
        lang = detect_indic_language("नमस्ते, आपका बैंक खाता ब्लॉक हो गया है")
        assert lang == "hi"

    def test_detect_marathi(self):
        lang = detect_indic_language("लगेच ५०००० रुपये पाठवा या नंबरवर")
        assert lang == "mr"

    def test_detect_tamil(self):
        lang = detect_indic_language("உங்கள் கணக்கு முடக்கப்பட்டுள்ளது, ஓடிபி சொல்லுங்க")
        assert lang == "ta"

    def test_detect_telugu(self):
        lang = detect_indic_language("బ్యాంకు మేనేజర్ మాట్లాడుతున్నాను, ఓటీపీ చెప్పండి")
        assert lang == "te"

    def test_detect_bengali(self):
        lang = detect_indic_language("টাকা পাঠান অবিলম্বে, পুলিশ আসছে")
        assert lang == "bn"

    def test_detect_gujarati(self):
        lang = detect_indic_language("તરત જ પૈસા મોકલો, અકસ્માત થયો છે")
        assert lang == "gu"

    def test_detect_punjabi(self):
        lang = detect_indic_language("ਬੈਂਕ ਅਫਸਰ ਬੋਲ ਰਿਹਾ ਹਾਂ, ਓਟੀਪੀ ਦੱਸੋ")
        assert lang == "pa"

    def test_detect_english(self):
        lang = detect_indic_language("Please transfer the money to my UPI immediately")
        assert lang == "en"


class TestIndicIntentAndTacticNLP:
    """Verifies intent and tactic detection across native regional languages."""

    def test_marathi_extortion_scam(self):
        text = "आई माझा अपघात झाला आहे, लगेच पैसे पाठवा पोलीस ठाण्यात!"
        res = intent_engine.analyze_transcript(text)
        assert res["detected_intent"] in ["MONEY_TRANSFER", "EMERGENCY"]
        assert "URGENCY" in res["detected_tactics"]
        assert res["detected_language"] == "mr"
        assert res["is_high_risk"] is True

    def test_tamil_bank_otp_scam(self):
        text = "உங்கள் கணக்கு முடக்கப்பட்டுள்ளது, உடனடியாக ஓடிபி சொல்லுங்க!"
        res = intent_engine.analyze_transcript(text)
        assert res["detected_intent"] == "OTP_REQUEST"
        assert "URGENCY" in res["detected_tactics"]
        assert res["detected_language"] == "ta"
        assert res["is_high_risk"] is True

    def test_telugu_authority_scam(self):
        text = "నేను పోలీస్ స్టేషన్ నుండి మాట్లాడుతున్నాను, వెంటనే డబ్బులు పంపండి!"
        res = intent_engine.analyze_transcript(text)
        assert res["detected_intent"] in ["MONEY_TRANSFER", "EMERGENCY"]
        assert "URGENCY" in res["detected_tactics"]
        assert res["detected_language"] == "te"
        assert res["is_high_risk"] is True

    def test_bengali_otp_harvesting(self):
        text = "আমি ব্যাংক ম্যানেজার, আপনার ওটিপি বলুন এখনি!"
        res = intent_engine.analyze_transcript(text)
        assert res["detected_intent"] in ["OTP_REQUEST", "BANK_VERIFICATION"]
        assert "AUTHORITY" in res["detected_tactics"]
        assert res["detected_language"] == "bn"
        assert res["is_high_risk"] is True

    def test_gujarati_emergency_scam(self):
        text = "હોસ્પિટલમાં દાખલ છે, તરત જ પૈસા મોકલો!"
        res = intent_engine.analyze_transcript(text)
        assert res["detected_intent"] in ["MONEY_TRANSFER", "EMERGENCY"]
        assert "URGENCY" in res["detected_tactics"]
        assert res["detected_language"] == "gu"
        assert res["is_high_risk"] is True

    def test_punjabi_bank_otp_scam(self):
        text = "ਬੈਂਕ ਅਫਸਰ, ਓਟੀਪੀ ਦੱਸੋ ਹੁਣੇ ਨਹੀਂ ਤਾਂ ਅਕਾਊਂਟ ਬੰਦ!"
        res = intent_engine.analyze_transcript(text)
        assert res["detected_intent"] in ["OTP_REQUEST", "BANK_VERIFICATION"]
        assert "AUTHORITY" in res["detected_tactics"]
        assert res["detected_language"] == "pa"
        assert res["is_high_risk"] is True

    def test_benign_indic_conversation(self):
        text = "आज संध्याकाळी आपण जेवायला जाऊया, काय ठरलं?"
        res = intent_engine.analyze_transcript(text)
        assert res["detected_intent"] == "NORMAL_CONVERSATION"
        assert len(res["detected_tactics"]) == 0
        assert res["is_high_risk"] is False


class TestLoopbackAudioStreamer:
    """Verifies audio PCM chunk generation and scenario loopback formatting."""

    def test_pcm_chunk_byte_length(self):
        """2 seconds of 16kHz 16-bit mono audio must be exactly 64,000 bytes."""
        pcm = LiveLoopbackAudioStreamer.generate_pcm_chunk(duration_sec=2.0, sample_rate=16000)
        assert len(pcm) == 64000  # 16000 samples * 2 sec * 2 bytes/sample

    def test_format_audio_payload_structure(self):
        """Loopback payload must contain all fields required by WebSocket router."""
        frame_meta = {"risk_override": 75, "synth_prob": 0.85, "speaker_sim": 0.40, "text": "Test speech"}
        payload = LiveLoopbackAudioStreamer.format_audio_payload(
            session_id="loopback-sess-01",
            seq=1,
            frame_meta=frame_meta,
        )
        assert payload["session_id"] == "loopback-sess-01"
        assert payload["sequence_number"] == 1
        assert "audio_chunk_b64" in payload
        assert payload["sample_rate"] == 16000
        assert payload["simulated_evidence"]["risk_score"] == 75

    def test_stream_scenario_loopback_all_profiles(self):
        """All 5 scenario profiles must generate valid non-empty frame sequences."""
        for sc_id in [1, 2, 3, 4, 5]:
            payloads = stream_scenario_loopback(session_id=f"test-sc-{sc_id}", scenario_id=sc_id)
            assert len(payloads) >= 3
            assert payloads[0]["sequence_number"] == 1
            assert len(payloads[0]["audio_chunk_b64"]) > 1000

    def test_indic_e2e_pipeline_processing(self):
        """MultiEvidencePipeline successfully aggregates Indic text transcript."""
        pipeline = MultiEvidencePipeline()
        res = pipeline.process_chunk(
            pcm_b64="AA==",
            simulated_evidence={
                "transcript": "लगेच पैसे पाठवा, पोलीस ठाण्यात अडकलो आहे!",
                "synthetic_prob": 0.88,
                "speaker_similarity": 0.42,
            },
        )
        assert res["transcript"] == "लगेच पैसे पाठवा, पोलीस ठाण्यात अडकलो आहे!"
        assert res["intent"] in ["MONEY_TRANSFER", "EMERGENCY"]
        assert "URGENCY" in res["tactics"]
        assert res["synthetic_prob"] == 0.88

