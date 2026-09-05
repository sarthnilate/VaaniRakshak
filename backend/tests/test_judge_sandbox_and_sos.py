# ============================================================
# VAANIRAKSHAK — Test Suite: Judge Sandbox & Citizen Emergency SOS
# Phase 13 Verification
# ============================================================
import io
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.emergency.citizen_sos import citizen_sos_dispatcher


@pytest.fixture(autouse=True)
def reset_sos_history():
    """Reset SOS dispatcher history before each test."""
    citizen_sos_dispatcher.clear_history()
    yield
    citizen_sos_dispatcher.clear_history()


@pytest.fixture
def client():
    return TestClient(app)


class TestIndicTextSandbox:
    """Tests for the interactive Indic text analysis sandbox endpoint."""

    def test_hindi_otp_scam_detection(self, client):
        resp = client.post(
            "/api/v1/sandbox/analyze-text",
            json={"text": "आपका SBI खाता तुरंत बंद हो जाएगा, OTP शेयर करें"}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["detected_language"] == "hi"
        assert data["primary_intent"] == "OTP_REQUEST"
        assert "URGENCY" in data["tactics"]
        assert data["scam_score"] >= 60
        assert data["is_fraud"] is True

    def test_marathi_extortion_detection(self, client):
        resp = client.post(
            "/api/v1/sandbox/analyze-text",
            json={"text": "तुमचे बँक खाते त्वरित ब्लॉक केले जाईल, व्हेरिफिकेशनसाठी ओटीपी पाठवा."}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["detected_language"] == "mr"
        assert data["primary_intent"] != "NORMAL_CONVERSATION"
        assert data["is_fraud"] is True

    def test_tamil_otp_scam_detection(self, client):
        resp = client.post(
            "/api/v1/sandbox/analyze-text",
            json={"text": "உங்கள் வங்கி கணக்கு முடக்கப்படும், சரிபார்க்க உடனே OTP பகிரவும்."}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["detected_language"] == "ta"
        assert data["primary_intent"] != "NORMAL_CONVERSATION"
        assert data["is_fraud"] is True

    def test_legitimate_conversation_safe(self, client):
        resp = client.post(
            "/api/v1/sandbox/analyze-text",
            json={"text": "Hello dad, reaching home by 7 PM. Please take your medicine on time."}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["primary_intent"] == "NORMAL_CONVERSATION"
        assert data["is_fraud"] is False
        assert data["scam_score"] <= 30

    def test_empty_text_returns_400(self, client):
        resp = client.post(
            "/api/v1/sandbox/analyze-text",
            json={"text": "   "}
        )
        assert resp.status_code == 400


class TestAudioSandbox:
    """Tests for multi-pipeline audio ingestion and evaluation."""

    def test_pcm_audio_upload_analysis(self, client):
        fake_pcm = io.BytesIO(b"\x00" * 64000)
        files = {"file": ("call_sample.wav", fake_pcm, "audio/wav")}
        resp = client.post("/api/v1/sandbox/analyze-audio", files=files)
        assert resp.status_code == 200
        data = resp.json()
        assert data["filename"] == "call_sample.wav"
        assert data["file_size_bytes"] == 64000
        assert data["duration_estimate_sec"] == 2.0
        assert "antispoof_score" in data
        assert "speaker_similarity" in data
        assert "composite_risk_score" in data
        assert data["action_recommended"] in ["MONITOR", "WARN", "ALERT", "BLOCK"]

    def test_audio_analysis_with_target_speaker(self, client):
        fake_pcm = io.BytesIO(b"\x00" * 64000)
        files = {"file": ("son_call.wav", fake_pcm, "audio/wav")}
        resp = client.post(
            "/api/v1/sandbox/analyze-audio",
            files=files,
            data={"target_speaker_id": "spk_rahul_son"}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["speaker_profile_matched"] == "Rahul (Son)"

    def test_empty_audio_file_returns_400(self, client):
        empty_file = io.BytesIO(b"")
        files = {"file": ("empty.wav", empty_file, "audio/wav")}
        resp = client.post("/api/v1/sandbox/analyze-audio", files=files)
        assert resp.status_code == 400


class TestCitizenEmergencySOS:
    """Tests for family contact emergency broadcast dispatcher."""

    def test_sos_trigger_critical_risk(self, client):
        resp = client.post(
            "/api/v1/emergency/sos-trigger",
            json={
                "session_id": "sess_test_sos_01",
                "suspect_number": "+91-9876543210",
                "risk_score": 94,
                "threat_category": "AI_VOICE_CLONING_EXTORTION",
            }
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["alert_id"].startswith("SOS-")
        assert data["suspect_number"] == "+91-9876543210"
        assert data["peak_risk_score"] == 94
        assert data["action_taken"] == "CALL_TERMINATED_AND_FAMILY_ALERTED"
        assert len(data["recipients"]) == 2
        # Verify dual-language alert content
        assert "94/100" in data["sms_content_en"]
        assert "AI_VOICE_CLONING_EXTORTION" in data["sms_content_en"]
        assert "वाणीरक्षक चेतावनी" in data["sms_content_hi"]
        assert "1930" in data["sms_content_hi"]

    def test_sos_trigger_warning_risk(self, client):
        resp = client.post(
            "/api/v1/emergency/sos-trigger",
            json={
                "session_id": "sess_test_sos_02",
                "suspect_number": "+91-7890123456",
                "risk_score": 82,
                "threat_category": "DIGITAL_ARREST_SCAM",
            }
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["action_taken"] == "FAMILY_WARNING_DISPATCHED"

    def test_sos_history_chronological(self, client):
        client.post(
            "/api/v1/emergency/sos-trigger",
            json={
                "session_id": "sess_hist_1",
                "suspect_number": "+91-9111111111",
                "risk_score": 95,
            }
        )
        client.post(
            "/api/v1/emergency/sos-trigger",
            json={
                "session_id": "sess_hist_2",
                "suspect_number": "+91-9222222222",
                "risk_score": 91,
            }
        )

        resp = client.get("/api/v1/emergency/sos-history")
        assert resp.status_code == 200
        history = resp.json()
        assert len(history) == 2
        assert history[0]["session_id"] == "sess_hist_2"  # Newest first
        assert history[1]["session_id"] == "sess_hist_1"


class TestCitizenSOSDispatcherDirect:
    """Unit tests on the Python CitizenSOSDispatcher service directly."""

    def test_dispatch_custom_contacts(self):
        custom_contacts = [
            {
                "contact_id": "contact_advocate",
                "name": "Legal Counsel",
                "phone_number": "+91-9899999999",
                "relation": "Advocate",
            }
        ]
        alert = citizen_sos_dispatcher.dispatch_emergency_sos(
            session_id="sess_custom_contacts",
            suspect_number="+91-9000000000",
            risk_score=96,
            contacts=custom_contacts,
        )
        assert len(alert.recipients) == 1
        assert alert.recipients[0].name == "Legal Counsel"
        assert alert.recipients[0].relation == "Advocate"
        assert alert.recipients[0].status == "DELIVERED"
