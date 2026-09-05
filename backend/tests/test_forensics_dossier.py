"""
============================================================
Phase 10 — Forensics Dossier & Carrier Telephony Tests
============================================================
Verifies:
  - Evidentiary dossier generation with SHA-256 cryptographic sealing
  - Single-bit / single-byte tampering detection across evidence chains
  - I4C-1930 CyberCrime portal compliance schema
  - Courtroom-grade Markdown export (Section 65B Indian Evidence Act)
  - Carrier SIP Trunk call registration, telemetry & automated teardown
  - REST API endpoint integration
"""
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.services.forensics.dossier_generator import (
    ForensicDossierGenerator,
    generate_session_dossier,
    verify_dossier_integrity,
)
from backend.services.carrier.sip_trunk_adapter import (
    CarrierSipTrunkAdapter,
)

SAMPLE_FRAMES = [
    {
        "risk_score": 25,
        "synthetic_prob": 0.15,
        "speaker_similarity": 0.88,
        "action": "MONITOR",
        "tactics": [],
        "transcript": "Hello, is this Rajesh speaking?",
        "is_fraud": False,
    },
    {
        "risk_score": 62,
        "synthetic_prob": 0.78,
        "speaker_similarity": 0.45,
        "action": "WARN",
        "tactics": ["urgency"],
        "transcript": "Papa, I am in big trouble at the police station!",
        "is_fraud": True,
    },
    {
        "risk_score": 94,
        "synthetic_prob": 0.94,
        "speaker_similarity": 0.38,
        "action": "BLOCK",
        "tactics": ["urgency", "financial_fraud"],
        "transcript": "Send 50,000 rupees immediately to this UPI ID or they will arrest me!",
        "is_fraud": True,
    },
]


class TestForensicDossierGenerator:
    """Tests for core forensic dossier generation and sealing."""

    def test_generate_dossier_structure(self):
        """Dossier must contain all mandatory evidentiary and chain-of-custody keys."""
        dossier = generate_session_dossier(
            session_id="test-session-101",
            caller_number="+91-9876543210",
            callee_number="+91-9123456780",
            frames=SAMPLE_FRAMES,
        )

        assert dossier["session_id"] == "test-session-101"
        assert dossier["case_reference"].startswith("I4C-1930-")
        assert dossier["dossier_id"].startswith("VAANI-DOSSIER-2026-")
        assert "cryptographic_seal" in dossier
        assert dossier["cryptographic_seal"]["algorithm"] == "SHA-256"
        assert len(dossier["cryptographic_seal"]["evidence_hash"]) == 64
        assert len(dossier["chronological_evidence_chain"]) == 3
        assert dossier["metadata"]["caller_number"] == "+91-9876543210"

    def test_sha256_cryptographic_seal_deterministic(self):
        """Identical evidence chains must produce identical SHA-256 digest."""
        hash1 = ForensicDossierGenerator.compute_evidence_hash(SAMPLE_FRAMES)
        hash2 = ForensicDossierGenerator.compute_evidence_hash(SAMPLE_FRAMES)
        assert hash1 == hash2

    def test_unaltered_dossier_passes_verification(self):
        """An authentic, untampered dossier must pass integrity verification."""
        dossier = generate_session_dossier(
            session_id="verify-sess-01",
            frames=SAMPLE_FRAMES,
        )
        assert verify_dossier_integrity(dossier) is True

    def test_tamper_detection_on_altered_risk_score(self):
        """Modifying a single risk score in the evidence chain must trigger tamper alert."""
        dossier = generate_session_dossier(
            session_id="tamper-sess-01",
            frames=SAMPLE_FRAMES,
        )
        assert verify_dossier_integrity(dossier) is True

        # Malicious actor tries to edit risk score to cover tracks
        dossier["chronological_evidence_chain"][2]["risk_score"] = 15

        # Must fail cryptographic verification
        assert verify_dossier_integrity(dossier) is False

    def test_tamper_detection_on_altered_transcript(self):
        """Modifying a single character of transcript must invalidate seal."""
        dossier = generate_session_dossier(
            session_id="tamper-sess-02",
            frames=SAMPLE_FRAMES,
        )
        assert verify_dossier_integrity(dossier) is True

        # Malicious actor changes transcript text
        dossier["chronological_evidence_chain"][1]["transcript"] += "."
        assert verify_dossier_integrity(dossier) is False

    def test_threat_level_critical_for_synthetic_voice(self):
        """Dossier must flag CRITICAL and AI Voice Cloning when synthetic probability >= 0.8."""
        dossier = generate_session_dossier(
            session_id="critical-synth-sess",
            frames=SAMPLE_FRAMES,
        )
        assert dossier["forensic_summary"]["overall_threat_level"] == "CRITICAL"
        assert "AI Voice Cloning" in dossier["forensic_summary"]["primary_fraud_vector"]
        assert dossier["forensic_summary"]["intervention_triggered"] is True

    def test_threat_level_low_for_benign_call(self):
        """Dossier for safe conversation must evaluate to LOW threat level."""
        benign_frames = [
            {"risk_score": 5, "synthetic_prob": 0.04, "speaker_similarity": 0.95, "action": "MONITOR", "transcript": "Hello mom"}
        ]
        dossier = generate_session_dossier(
            session_id="benign-sess",
            frames=benign_frames,
        )
        assert dossier["forensic_summary"]["overall_threat_level"] == "LOW"
        assert dossier["forensic_summary"]["intervention_triggered"] is False

    def test_i4c_portal_export_schema(self):
        """Dossier must generate I4C 1930 portal submission compliant payload."""
        dossier = generate_session_dossier(
            session_id="i4c-export-sess",
            caller_number="+91-9988776655",
            callee_number="+91-8877665544",
            frames=SAMPLE_FRAMES,
        )
        i4c = dossier["i4c_portal_export"]
        assert i4c["suspect_telecom_cli"] == "+91-9988776655"
        assert i4c["complainant_target"] == "+91-8877665544"
        assert i4c["national_helpline"] == "1930"
        assert len(i4c["hash_signature"]) == 64

    def test_markdown_courtroom_report_format(self):
        """Markdown output must include Section 65B certificate and tables."""
        dossier = generate_session_dossier(
            session_id="md-sess",
            frames=SAMPLE_FRAMES,
        )
        md = ForensicDossierGenerator.to_markdown(dossier)
        assert "FORENSIC CYBERCRIME INCIDENT DOSSIER" in md
        assert "Section 65B" in md
        assert "SHA-256" in md
        assert "| Offset | Risk |" in md
        assert "Send 50,000 rupees" in md


class TestCarrierSipAdapter:
    """Tests for Tier-3 Carrier SIP trunk integration."""

    def test_register_carrier_call_circuit(self):
        """Registers SIP INVITE with telecom network telemetry."""
        adapter = CarrierSipTrunkAdapter(carrier_name="Jio Telephony Core")
        event = adapter.register_call({
            "call_id": "sip-circ-101",
            "calling_party": "+91-9876543210",
            "called_party": "+91-1122334455",
            "codec": "AMR-WB/16000",
            "cell_tower_cgi": "404-45-1200-9901",
            "packet_loss_pct": 0.4,
            "jitter_ms": 2.5,
        })
        assert event.call_id == "sip-circ-101"
        assert event.carrier_name == "Jio Telephony Core"
        assert event.codec == "AMR-WB/16000"

        # Telemetry should be queryable
        telem = adapter.get_circuit_telemetry("sip-circ-101")
        assert telem is not None
        assert telem["network_telemetry"]["packet_loss_pct"] == 0.4

    def test_carrier_emergency_teardown(self):
        """Triggering teardown sends SIP 603 Decline and closes circuit."""
        adapter = CarrierSipTrunkAdapter()
        adapter.register_call({"call_id": "teardown-call-01"})
        
        result = adapter.trigger_carrier_teardown("teardown-call-01", reason="CRITICAL_VOICE_CLONE_DETECTED")
        assert result.status == "CIRCUIT_TERMINATED"
        assert result.sip_response_code == 603

        # Circuit should now be closed
        assert adapter.get_circuit_telemetry("teardown-call-01") is None

    def test_carrier_teardown_missing_call(self):
        """Teardown on closed or non-existent circuit returns code 481."""
        adapter = CarrierSipTrunkAdapter()
        result = adapter.trigger_carrier_teardown("non-existent-call")
        assert result.status == "CIRCUIT_NOT_FOUND_OR_ALREADY_CLOSED"
        assert result.sip_response_code == 481


class TestForensicsAPIEndpoints:
    """Tests for REST API endpoints in /forensics and /carrier."""

    def test_api_generate_and_get_dossier(self):
        """Generate sealed dossier via API and retrieve by session_id."""
        with TestClient(app) as client:
            # Generate
            post_res = client.post("/api/v1/forensics/dossier/generate", json={
                "session_id": "api-sess-001",
                "caller_number": "+91-9000000001",
                "callee_number": "+91-9000000002",
                "frames": SAMPLE_FRAMES,
                "operator_notes": "Live test scenario run",
            })
            assert post_res.status_code == 200
            data = post_res.json()
            assert data["status"] == "SEALED"
            assert "sha256_seal" in data
            assert data["case_reference"].startswith("I4C-1930-")

            # Get
            get_res = client.get("/api/v1/forensics/dossier/api-sess-001")
            assert get_res.status_code == 200
            get_data = get_res.json()
            assert get_data["session_id"] == "api-sess-001"
            assert get_data["cryptographic_seal"]["evidence_hash"] == data["sha256_seal"]

    def test_api_download_markdown(self):
        """Download dossier as courtroom-grade markdown file."""
        with TestClient(app) as client:
            res = client.get("/api/v1/forensics/dossier/api-sess-001/download?format=markdown")
            assert res.status_code == 200
            assert "text/markdown" in res.headers["content-type"]
            assert "attachment;" in res.headers["content-disposition"]
            assert "# 🏛️ FORENSIC CYBERCRIME INCIDENT DOSSIER" in res.text

    def test_api_download_json(self):
        """Download dossier as raw JSON file."""
        with TestClient(app) as client:
            res = client.get("/api/v1/forensics/dossier/api-sess-001/download?format=json")
            assert res.status_code == 200
            assert "application/json" in res.headers["content-type"]
            d = res.json()
            assert "cryptographic_seal" in d

    def test_api_verify_dossier_unaltered(self):
        """Verify unmodified dossier passes API validation."""
        with TestClient(app) as client:
            dossier = generate_session_dossier(session_id="api-verify-sess", frames=SAMPLE_FRAMES)
            res = client.post("/api/v1/forensics/dossier/verify", json=dossier)
            assert res.status_code == 200
            assert res.json()["is_valid"] is True
            assert res.json()["status"] == "UNALTERED_EVIDENCE"

    def test_api_verify_dossier_tampered(self):
        """Verify modified dossier fails API validation."""
        with TestClient(app) as client:
            dossier = generate_session_dossier(session_id="api-verify-sess-2", frames=SAMPLE_FRAMES)
            # Tamper
            dossier["chronological_evidence_chain"][0]["risk_score"] = 99
            res = client.post("/api/v1/forensics/dossier/verify", json=dossier)
            assert res.status_code == 200
            assert res.json()["is_valid"] is False
            assert res.json()["status"] == "TAMPERING_OR_CORRUPTION_DETECTED"

    def test_api_carrier_lifecycle(self):
        """Carrier SIP webhook registration followed by automated teardown."""
        with TestClient(app) as client:
            # Register SIP call
            reg_res = client.post("/api/v1/carrier/sip_event", json={
                "call_id": "carrier-api-call-99",
                "calling_party": "+91-9999988888",
                "called_party": "+91-7777766666",
            })
            assert reg_res.status_code == 200
            assert reg_res.json()["status"] == "CALL_CIRCUIT_ACTIVE"

            # Check telemetry
            telem_res = client.get("/api/v1/carrier/telemetry/carrier-api-call-99")
            assert telem_res.status_code == 200
            assert telem_res.json()["calling_party"] == "+91-9999988888"

            # Teardown
            tear_res = client.post("/api/v1/carrier/teardown", json={
                "call_id": "carrier-api-call-99",
                "reason": "CRITICAL_FRAUD",
            })
            assert tear_res.status_code == 200
            assert tear_res.json()["status"] == "CIRCUIT_TERMINATED"
            assert tear_res.json()["sip_response_code"] == 603
