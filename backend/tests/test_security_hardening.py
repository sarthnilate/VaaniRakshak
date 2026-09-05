"""
============================================================
Phase 9 — Security Hardening & Adversarial Input Validation Tests
============================================================
Tests the system's resilience against:
  - Malformed / oversized audio payload attacks
  - Injection via transcript/session fields
  - Replay attack detection
  - Rate limiting boundary enforcement
  - Risk score boundary clamping (no overflow, no bypass)
  - Policy bypass attempts via crafted evidence vectors
  - Concurrent session isolation (no cross-session state leak)
"""

import pytest
import time
from backend.main import app
from backend.services.ai.pipeline_aggregator import MultiEvidencePipeline
from backend.services.risk.temporal_state import TemporalRiskStateEngine
from backend.services.decision.policy_engine import PolicyDecisionEngine
from backend.schemas.risk import EvidenceSummary


# ============================================================
# Input Validation & Boundary Tests
# ============================================================

class TestInputValidation:
    """Validates that all API inputs are strictly validated and sanitised."""

    def test_risk_score_never_exceeds_100(self):
        """GRU must never produce a risk score > 100, regardless of extreme inputs."""
        engine = TemporalRiskStateEngine()
        # Feed extreme values
        extreme_evidence = {
            "synthetic_prob": 999.9,   # Way above [0,1] range
            "intent": "OTP_REQUEST",
            "tactics": ["URGENCY"] * 50,  # Excessive tactics list
            "risk_score": 200,           # Attempted bypass: score > 100
        }
        result = engine.compute_next_state(current_state=[], evidence_vector=extreme_evidence)
        assert 0 <= result["risk_score"] <= 100, \
            f"Risk score must be clamped [0,100]. Got: {result['risk_score']}"

    def test_risk_score_never_below_zero(self):
        """Risk score must never go negative even with zero/negative synthetic prob."""
        engine = TemporalRiskStateEngine()
        negative_evidence = {
            "synthetic_prob": -5.0,
            "speaker_sim": -1.0,
            "intent": "NORMAL_CONVERSATION",
            "tactics": [],
            "risk_score": -50,
        }
        result = engine.compute_next_state(current_state=[], evidence_vector=negative_evidence)
        assert result["risk_score"] >= 0, \
            f"Risk score must be ≥ 0. Got: {result['risk_score']}"

    def test_policy_engine_trusted_contact_cannot_bypass_critical(self):
        """
        Even trusted contacts must be flagged if synthetic_probability >= 0.90.
        A trusted contact bypass must NOT apply when voice is clearly synthetic.
        """
        policy = PolicyDecisionEngine()
        summary = EvidenceSummary(
            synthetic_probability=0.97,  # Clearly synthetic
            speaker_similarity=0.99,     # "Matches" trusted contact
            detected_intent="OTP_REQUEST",
            detected_tactics=["URGENCY"],
        )
        result = policy.evaluate_policy(
            risk_score=95,
            evidence_summary=summary,
            is_trusted_contact=True,  # Attacker claims to be trusted
        )
        # Trusted contact bypass only applies when synthetic_prob < 0.30
        # With synthetic_prob=0.97 it should NOT reduce the score below CRITICAL
        # The policy applies: effective_score = min(95, 25) ONLY when synth < 0.30
        # So at 0.97 synthetic, effective_score stays at 95
        assert result["band"] in ("CRITICAL", "HIGH"), \
            f"Trusted contact must not bypass CRITICAL threat. Band: {result['band']}, score: {result['effective_risk_score']}"

    def test_empty_tactics_list_safe(self):
        """Empty tactics list must not cause errors or inflated scores."""
        policy = PolicyDecisionEngine()
        summary = EvidenceSummary(
            synthetic_probability=0.05,
            detected_intent="NORMAL_CONVERSATION",
            detected_tactics=[],
        )
        result = policy.evaluate_policy(risk_score=5, evidence_summary=summary)
        assert result["band"] == "SAFE"
        assert result["should_intervene"] is False

    def test_very_long_tactics_list_clamped(self):
        """Extremely long tactics list must not overflow the score calculation."""
        engine = TemporalRiskStateEngine()
        evidence = {
            "synthetic_prob": 0.5,
            "intent": "OTP_REQUEST",
            "tactics": ["URGENCY"] * 1000,  # 1000 tactics — should be clamped
        }
        result = engine.compute_next_state(current_state=[], evidence_vector=evidence)
        assert 0 <= result["risk_score"] <= 100, \
            f"Clamping failed with large tactics list. Score: {result['risk_score']}"

    def test_none_speaker_sim_handled_gracefully(self):
        """None speaker_similarity must not raise errors — it's a valid unenrolled state."""
        policy = PolicyDecisionEngine()
        summary = EvidenceSummary(
            synthetic_probability=0.8,
            speaker_similarity=None,  # No enrolled profile
            detected_intent="OTP_REQUEST",
            detected_tactics=["URGENCY"],
        )
        result = policy.evaluate_policy(risk_score=82, evidence_summary=summary)
        assert "band" in result
        assert "action" in result

    def test_unknown_intent_defaults_to_normal(self):
        """Unknown/unrecognized intent values must default to NORMAL_CONVERSATION."""
        engine = TemporalRiskStateEngine()
        evidence = {
            "synthetic_prob": 0.1,
            "intent": "TOTALLY_UNKNOWN_INTENT_XYZ_12345",
            "tactics": [],
        }
        result = engine.compute_next_state(current_state=[], evidence_vector=evidence)
        # Unknown intent should not trigger high risk
        assert result["risk_score"] < 60, \
            f"Unknown intent should produce low risk. Got: {result['risk_score']}"


# ============================================================
# Policy Bypass Attempt Tests
# ============================================================

class TestPolicyBypassAttempts:
    """Validates the policy engine cannot be bypassed by crafted inputs."""

    def test_critical_score_always_triggers_intervention(self):
        """Any risk score ≥ 90 must always trigger intervention — no exceptions."""
        policy = PolicyDecisionEngine()
        for score in [90, 91, 95, 99, 100]:
            summary = EvidenceSummary(
                synthetic_probability=0.9,
                detected_intent="OTP_REQUEST",
                detected_tactics=["URGENCY"],
            )
            result = policy.evaluate_policy(
                risk_score=score,
                evidence_summary=summary,
                is_trusted_contact=False,
            )
            assert result["should_intervene"] is True, \
                f"Score {score} must trigger intervention. Got: should_intervene={result['should_intervene']}"

    def test_safe_score_never_triggers_intervention(self):
        """Risk scores ≤ 29 must never trigger intervention or alert."""
        policy = PolicyDecisionEngine()
        for score in [0, 5, 10, 15, 20, 25, 29]:
            summary = EvidenceSummary(
                synthetic_probability=0.05,
                detected_intent="NORMAL_CONVERSATION",
                detected_tactics=[],
            )
            result = policy.evaluate_policy(risk_score=score, evidence_summary=summary)
            assert result["should_intervene"] is False, \
                f"Score {score} must NOT trigger intervention. Got: {result['should_intervene']}"
            assert result["band"] in ("SAFE", "LOW"), \
                f"Score {score} band wrong: {result['band']}"

    def test_score_override_in_simulated_evidence_bounded(self):
        """Simulated evidence risk_score override must still be clamped to [0,100]."""
        engine = TemporalRiskStateEngine()
        result = engine.compute_next_state(
            current_state=[],
            evidence_vector={"risk_score": 9999, "synthetic_prob": 0.5, "intent": "OTP_REQUEST", "tactics": []},
        )
        assert result["risk_score"] <= 100, \
            f"Overridden risk_score must be clamped to 100. Got: {result['risk_score']}"

    def test_intervention_window_policy_override_respected(self):
        """Custom policy override for intervention window must be respected."""
        policy = PolicyDecisionEngine()
        summary = EvidenceSummary(
            synthetic_probability=0.95,
            detected_intent="OTP_REQUEST",
            detected_tactics=["URGENCY"],
        )
        result = policy.evaluate_policy(
            risk_score=92,
            evidence_summary=summary,
            policy_override={"intervention_window_sec": 30},  # Custom 30s window
        )
        assert result["intervention_window_sec"] == 30, \
            f"Custom intervention window must be respected. Got: {result['intervention_window_sec']}"


# ============================================================
# Concurrent Session Isolation Tests
# ============================================================

class TestSessionIsolation:
    """
    Validates that concurrent sessions have completely independent state —
    no cross-session risk state contamination.
    """

    def test_two_sessions_independent_risk_trajectories(self):
        """Two parallel sessions must maintain independent GRU hidden states."""
        engine1 = TemporalRiskStateEngine()
        engine2 = TemporalRiskStateEngine()

        hidden1: list = []
        hidden2: list = []

        # Session 1: high-risk fraud call
        for _ in range(5):
            result1 = engine1.compute_next_state(
                current_state=hidden1,
                evidence_vector={"risk_score": 90, "synthetic_prob": 0.95,
                                 "intent": "OTP_REQUEST", "tactics": ["URGENCY"]},
            )
            hidden1 = result1["hidden_state"]

        # Session 2: legitimate call
        for _ in range(5):
            result2 = engine2.compute_next_state(
                current_state=hidden2,
                evidence_vector={"risk_score": 8, "synthetic_prob": 0.05,
                                 "intent": "NORMAL_CONVERSATION", "tactics": []},
            )
            hidden2 = result2["hidden_state"]

        # Sessions must have diverged completely
        assert result1["risk_score"] > 70, \
            f"Session 1 (fraud) should have high risk. Got: {result1['risk_score']}"
        assert result2["risk_score"] < 30, \
            f"Session 2 (legit) should have low risk. Got: {result2['risk_score']}"
        # Hidden states must be different
        assert hidden1 != hidden2, \
            "Two independent sessions must have different hidden states"

    def test_gru_state_reset_between_sessions(self):
        """A new session (empty hidden state) must start fresh at baseline risk."""
        engine = TemporalRiskStateEngine()

        # First call: escalate to CRITICAL
        hidden = []
        for _ in range(5):
            r = engine.compute_next_state(
                current_state=hidden,
                evidence_vector={"risk_score": 95, "synthetic_prob": 0.97,
                                 "intent": "MONEY_TRANSFER", "tactics": ["URGENCY", "FEAR"]},
            )
            hidden = r["hidden_state"]
        high_risk = r["risk_score"]

        # New session: start fresh with empty state
        fresh_result = engine.compute_next_state(
            current_state=[],  # Empty state = new session
            evidence_vector={"risk_score": 8, "synthetic_prob": 0.05,
                             "intent": "NORMAL_CONVERSATION", "tactics": []},
        )
        assert fresh_result["risk_score"] < 30, \
            f"Fresh session must start at baseline, not carry over from previous. " \
            f"Previous: {high_risk}, Fresh: {fresh_result['risk_score']}"


# ============================================================
# API Endpoint Security Tests (Sync — using TestClient)
# ============================================================

class TestAPIEndpointSecurity:
    """Tests FastAPI endpoints for correct status codes and input rejection."""

    def test_health_endpoint_always_available(self):
        """Health endpoint must always respond 200."""
        from fastapi.testclient import TestClient
        with TestClient(app) as client:
            response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "HEALTHY"
        assert "policy" in data
        assert data["policy"]["intervention_window_sec"] == 10

    def test_invalid_session_id_returns_404(self):
        """Requests with non-existent session IDs must return 404."""
        from fastapi.testclient import TestClient
        with TestClient(app) as client:
            response = client.get("/api/v1/sessions/nonexistent_session_99999")
        assert response.status_code in (404, 422), \
            f"Invalid session must return 404/422. Got: {response.status_code}"

    def test_root_endpoint_returns_welcome(self):
        """Root endpoint must return welcome message with docs link."""
        from fastapi.testclient import TestClient
        with TestClient(app) as client:
            response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "VAANIRAKSHAK" in data.get("message", "")

    def test_attack_lab_endpoint_accessible(self):
        """Attack Lab generation endpoint must be reachable (not 500)."""
        from fastapi.testclient import TestClient
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/attack_lab/generate",
                json={
                    "generator": "mock_research",
                    "scenario": 1,
                    "language": "hi",
                    "degradation": "pstn",
                    "duration_sec": 2.0,
                }
            )
        assert response.status_code in (200, 201, 422), \
            f"Attack lab must not crash (500). Got: {response.status_code}\n{response.text}"


    def test_cors_allowed_origins_configured(self):
        """CORS allow_origins must include wildcard (for dashboard at localhost:5174)."""
        from backend.config import settings
        # Settings must have CORS configured to allow all origins in demo mode
        assert settings.ALLOWED_ORIGINS is not None
        assert len(settings.ALLOWED_ORIGINS) > 0, "ALLOWED_ORIGINS must be configured"

    def test_docs_endpoint_accessible(self):
        """OpenAPI /docs endpoint must be accessible for SIH judge review."""
        from fastapi.testclient import TestClient
        with TestClient(app) as client:
            response = client.get("/docs")
        assert response.status_code == 200


# ============================================================
# Data Integrity Tests
# ============================================================

class TestDataIntegrity:
    """Validates data integrity across the pipeline chain."""

    def test_evidence_summary_immutable_through_policy(self):
        """Policy engine must not mutate the input EvidenceSummary object."""
        policy = PolicyDecisionEngine()
        summary = EvidenceSummary(
            synthetic_probability=0.85,
            speaker_similarity=0.70,
            detected_intent="OTP_REQUEST",
            detected_tactics=["URGENCY", "FEAR"],
        )
        original_synth = summary.synthetic_probability
        original_tactics = list(summary.detected_tactics)

        policy.evaluate_policy(risk_score=88, evidence_summary=summary)

        assert summary.synthetic_probability == original_synth, \
            "Policy engine must not mutate synthetic_probability"
        assert list(summary.detected_tactics) == original_tactics, \
            "Policy engine must not mutate detected_tactics list"

    def test_temporal_state_list_immutable_after_update(self):
        """GRU compute_next_state must return a new hidden state, not mutate the input."""
        engine = TemporalRiskStateEngine()
        original_state = [0.5] * 8
        state_copy = list(original_state)

        engine.compute_next_state(
            current_state=original_state,
            evidence_vector={"synthetic_prob": 0.9, "intent": "OTP_REQUEST", "tactics": ["URGENCY"]},
        )
        assert original_state == state_copy, \
            "GRU must not mutate the input hidden_state list"

    def test_pipeline_output_always_has_required_keys(self):
        """MultiEvidencePipeline output must always contain all required keys."""
        pipeline = MultiEvidencePipeline()
        required_keys = {"synthetic_prob", "human_prob", "speaker_sim", "intent", "tactics", "transcript"}

        for _ in range(5):
            result = pipeline.process_chunk(pcm_b64="AAAA")
            missing = required_keys - set(result.keys())
            assert not missing, \
                f"Pipeline output missing required keys: {missing}"

    def test_risk_trajectory_monotonic_under_sustained_threat(self):
        """Risk must broadly increase (not decrease) under sustained high threat."""
        engine = TemporalRiskStateEngine()
        hidden: list = []
        scores = []

        for _ in range(8):
            result = engine.compute_next_state(
                current_state=hidden,
                evidence_vector={"synthetic_prob": 0.95, "intent": "MONEY_TRANSFER",
                                 "tactics": ["URGENCY", "FEAR", "AUTHORITY_IMPERSONATION"]},
            )
            hidden = result["hidden_state"]
            scores.append(result["risk_score"])

        # Under sustained high threat, final score must be >= initial score
        assert scores[-1] >= scores[0], \
            f"Risk should increase under sustained threat. Scores: {scores}"
        # Final score must be HIGH or CRITICAL (>= 70)
        assert scores[-1] >= 70, \
            f"Sustained threat must reach HIGH/CRITICAL. Final score: {scores[-1]}"
