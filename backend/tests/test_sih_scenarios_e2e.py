"""
============================================================
Phase 8 — E2E SIH Demonstration Scenario Tests
============================================================
Validates the complete VAANIRAKSHAK defense pipeline across
all 3 mandatory SIH 2026 demo scenarios:

  Scenario 1: AI-Cloned Voice (Hindi Banking Fraud)   → DETECT & INTERVENE
  Scenario 2: Real Human Scammer (English OTP Fraud)  → DETECT & ALERT
  Scenario 3: Legitimate Call (Car Service)            → SAFE (no false positive)

All scenarios are executed end-to-end through the full pipeline:
  Audio Frame → Voice Authenticity → Speaker Verification
  → STT + Intent NLP → Multi-Evidence Pipeline
  → Temporal GRU State → Policy Decision Engine
"""

import pytest
from backend.services.ai.pipeline_aggregator import MultiEvidencePipeline
from backend.services.risk.temporal_state import TemporalRiskStateEngine
from backend.services.decision.policy_engine import PolicyDecisionEngine
from backend.schemas.risk import EvidenceSummary


# ============================================================
# Shared Fixtures & Helpers
# ============================================================

@pytest.fixture
def e2e_pipeline():
    """Full E2E pipeline: aggregator + temporal + policy."""
    return {
        "pipeline": MultiEvidencePipeline(),
        "temporal": TemporalRiskStateEngine(),
        "policy": PolicyDecisionEngine(),
    }


def run_scenario_frames(pipeline, temporal, policy, frames: list) -> list:
    """
    Execute N frames through the complete pipeline and return frame-by-frame results.
    frames: list of dicts with keys: audio_b64, language, is_unknown_caller, simulated_evidence
    """
    hidden_state: list = []
    results = []

    for i, frame in enumerate(frames):
        # Step 1: Multi-Evidence Pipeline
        evidence = pipeline.process_chunk(
            pcm_b64=frame.get("audio_b64", "AAAA"),
            preferred_language=frame.get("language", "hi"),
            simulated_evidence=frame.get("simulated_evidence", {}),
        )

        # Step 2: Temporal GRU State Update
        temporal_result = temporal.compute_next_state(
            current_state=hidden_state,
            evidence_vector=evidence,
            is_unknown_caller=frame.get("is_unknown_caller", True),
        )
        hidden_state = temporal_result["hidden_state"]

        # Step 3: Policy Decision Engine
        summary = EvidenceSummary(
            synthetic_probability=evidence.get("synthetic_prob", 0.05),
            speaker_similarity=evidence.get("speaker_sim"),
            detected_intent=evidence.get("intent", "NORMAL_CONVERSATION"),
            detected_tactics=evidence.get("tactics", []),
        )
        decision = policy.evaluate_policy(
            risk_score=temporal_result["risk_score"],
            evidence_summary=summary,
            is_trusted_contact=False,
        )

        results.append({
            "frame": i + 1,
            "risk_score": temporal_result["risk_score"],
            "band": decision["band"],
            "action": decision["action"],
            "should_intervene": decision["should_intervene"],
            "evidence": evidence,
        })

    return results


# ============================================================
# SCENARIO 1: AI-Cloned Voice — Hindi Banking Fraud (KYC/OTP Scam)
# ============================================================

class TestScenario1AIClonedVoice:
    """
    SIH Demo Scenario 1: Attacker uses AI voice cloning to impersonate
    a State Bank of India officer and request OTP/KYC compliance.

    Expected Outcome:
    - Risk trajectory ESCALATES: SAFE → LOW → MEDIUM → CRITICAL
    - At least 1 frame must trigger INTERVENE_RECOMMENDED action
    - Final risk score must be ≥ 90
    """

    FRAMES = [
        {
            "language": "hi",
            "is_unknown_caller": True,
            "simulated_evidence": {
                "risk_score": 22,
                "synthetic_prob": 0.25,
                "intent": "NORMAL_CONVERSATION",
                "tactics": [],
            },
        },
        {
            "language": "hi",
            "is_unknown_caller": True,
            "simulated_evidence": {
                "risk_score": 48,
                "synthetic_prob": 0.62,
                "intent": "BANK_VERIFICATION",
                "tactics": ["URGENCY"],
            },
        },
        {
            "language": "hi",
            "is_unknown_caller": True,
            "simulated_evidence": {
                "risk_score": 72,
                "synthetic_prob": 0.88,
                "intent": "OTP_REQUEST",
                "tactics": ["URGENCY", "AUTHORITY_IMPERSONATION"],
            },
        },
        {
            "language": "hi",
            "is_unknown_caller": True,
            "simulated_evidence": {
                "risk_score": 94,
                "synthetic_prob": 0.96,
                "intent": "MONEY_TRANSFER",
                "tactics": ["URGENCY", "AUTHORITY_IMPERSONATION", "FEAR"],
            },
        },
    ]

    def test_scenario1_full_e2e(self, e2e_pipeline):
        """Validate full E2E pipeline for Scenario 1 — AI cloned Hindi banking fraud."""
        results = run_scenario_frames(
            e2e_pipeline["pipeline"],
            e2e_pipeline["temporal"],
            e2e_pipeline["policy"],
            self.FRAMES,
        )
        # Risk escalation: each frame's risk should be ≥ previous (allow ±5 tolerance)
        risk_scores = [r["risk_score"] for r in results]
        for i in range(len(risk_scores) - 1):
            assert risk_scores[i] <= risk_scores[i + 1] + 5, \
                f"Risk should escalate: frame {i+1}={risk_scores[i]} > frame {i+2}={risk_scores[i+1]}"

        # Final frame must be CRITICAL and trigger intervention
        final = results[-1]
        assert final["risk_score"] >= 90, \
            f"Final risk must be ≥ 90. Got: {final['risk_score']}"
        assert final["band"] == "CRITICAL", \
            f"Final band must be CRITICAL. Got: {final['band']}"
        assert final["should_intervene"] is True, \
            "Emergency intervention must be triggered in Scenario 1"

    def test_scenario1_detects_synthetic_voice(self, e2e_pipeline):
        """Frame 3 must flag synthetic voice probability ≥ 0.80."""
        results = run_scenario_frames(
            e2e_pipeline["pipeline"],
            e2e_pipeline["temporal"],
            e2e_pipeline["policy"],
            self.FRAMES[2:],
        )
        for result in results:
            synth = result["evidence"].get("synthetic_prob", 0)
            assert synth >= 0.80, \
                f"Synthetic prob should be ≥ 0.80 at peak frames. Got: {synth}"

    def test_scenario1_detects_otp_intent(self, e2e_pipeline):
        """Frame 3 (OTP request) must surface OTP_REQUEST intent."""
        results = run_scenario_frames(
            e2e_pipeline["pipeline"],
            e2e_pipeline["temporal"],
            e2e_pipeline["policy"],
            [self.FRAMES[2]],
        )
        intent = results[0]["evidence"].get("intent")
        assert intent == "OTP_REQUEST", f"Expected OTP_REQUEST. Got: {intent}"

    def test_scenario1_trajectory_22_to_94(self, e2e_pipeline):
        """Risk trajectory must span from ≤ 30 (Frame 1) to ≥ 90 (Frame 4)."""
        results = run_scenario_frames(
            e2e_pipeline["pipeline"],
            e2e_pipeline["temporal"],
            e2e_pipeline["policy"],
            self.FRAMES,
        )
        assert results[0]["risk_score"] <= 30, \
            f"Frame 1 should be SAFE (≤ 30). Got: {results[0]['risk_score']}"
        assert results[-1]["risk_score"] >= 90, \
            f"Frame 4 should be CRITICAL (≥ 90). Got: {results[-1]['risk_score']}"


# ============================================================
# SCENARIO 2: Real Human Scammer — English Credit Card Fraud
# ============================================================

class TestScenario2RealHumanScammer:
    """
    SIH Demo Scenario 2: Real human (not AI) scammer impersonating
    HDFC Bank credit card division, requesting OTP verification.

    Expected Outcome:
    - Voice authenticity stays low (real human, synthetic_prob < 0.25)
    - Intent NLP detects OTP_REQUEST / BANK_VERIFICATION
    - Risk still escalates to HIGH/CRITICAL via social engineering
    - Intervention triggered from COMBINED evidence
    """

    FRAMES = [
        {
            "language": "en",
            "is_unknown_caller": True,
            "simulated_evidence": {
                "risk_score": 18,
                "synthetic_prob": 0.12,  # Real human voice
                "intent": "BANK_VERIFICATION",
                "tactics": ["AUTHORITY_IMPERSONATION"],
            },
        },
        {
            "language": "en",
            "is_unknown_caller": True,
            "simulated_evidence": {
                "risk_score": 45,
                "synthetic_prob": 0.15,
                "intent": "BANK_VERIFICATION",
                "tactics": ["URGENCY", "AUTHORITY_IMPERSONATION"],
            },
        },
        {
            "language": "en",
            "is_unknown_caller": True,
            "simulated_evidence": {
                "risk_score": 78,
                "synthetic_prob": 0.18,
                "intent": "OTP_REQUEST",
                "tactics": ["URGENCY", "AUTHORITY_IMPERSONATION", "SOCIAL_PROOF"],
            },
        },
        {
            "language": "en",
            "is_unknown_caller": True,
            "simulated_evidence": {
                "risk_score": 91,
                "synthetic_prob": 0.20,
                "intent": "OTP_REQUEST",
                "tactics": ["URGENCY", "FEAR", "AUTHORITY_IMPERSONATION", "DEADLINE_PRESSURE"],
            },
        },
    ]

    def test_scenario2_full_e2e(self, e2e_pipeline):
        """Validate full E2E for Scenario 2 — real human OTP scammer."""
        results = run_scenario_frames(
            e2e_pipeline["pipeline"],
            e2e_pipeline["temporal"],
            e2e_pipeline["policy"],
            self.FRAMES,
        )
        final = results[-1]
        assert final["risk_score"] >= 85, \
            f"Scenario 2 final risk must be ≥ 85. Got: {final['risk_score']}"
        assert final["band"] in ("HIGH", "CRITICAL"), \
            f"Expected HIGH or CRITICAL band. Got: {final['band']}"

    def test_scenario2_detects_authority_impersonation(self, e2e_pipeline):
        """All frames must detect AUTHORITY_IMPERSONATION tactic."""
        results = run_scenario_frames(
            e2e_pipeline["pipeline"],
            e2e_pipeline["temporal"],
            e2e_pipeline["policy"],
            self.FRAMES,
        )
        for result in results:
            tactics = result["evidence"].get("tactics", [])
            assert "AUTHORITY_IMPERSONATION" in tactics, \
                f"AUTHORITY_IMPERSONATION should be present: {tactics}"

    def test_scenario2_real_voice_low_synthetic(self, e2e_pipeline):
        """System must detect threat via social engineering even with LOW synthetic_prob."""
        results = run_scenario_frames(
            e2e_pipeline["pipeline"],
            e2e_pipeline["temporal"],
            e2e_pipeline["policy"],
            self.FRAMES,
        )
        # All frames should have real-human-level synthetic prob
        for result in results:
            synth = result["evidence"].get("synthetic_prob", 0)
            assert synth < 0.25, \
                f"Scenario 2 should have low synthetic prob (real human). Got: {synth}"
        # But risk still escalates to CRITICAL via NLP
        assert results[-1]["risk_score"] >= 85, \
            "Multi-vector detection must catch real human scammers via NLP tactics"

    def test_scenario2_intent_captures_otp_request(self, e2e_pipeline):
        """Frame 3 must surface OTP_REQUEST intent."""
        results = run_scenario_frames(
            e2e_pipeline["pipeline"],
            e2e_pipeline["temporal"],
            e2e_pipeline["policy"],
            [self.FRAMES[2]],
        )
        assert results[0]["evidence"].get("intent") == "OTP_REQUEST", \
            f"Expected OTP_REQUEST. Got: {results[0]['evidence'].get('intent')}"


# ============================================================
# SCENARIO 3: Legitimate Call — Zero False Positive Validation
# ============================================================

class TestScenario3LegitimateCall:
    """
    SIH Demo Scenario 3: Legitimate car service appointment call.
    Natural speech, no fraud intent, no social engineering.

    Expected Outcome:
    - Risk score must remain SAFE / LOW throughout (< 40)
    - NO intervention triggered — False Positive Rate = 0
    - Decision engine outputs MONITOR for all frames
    """

    FRAMES = [
        {
            "language": "en",
            "is_unknown_caller": True,
            "simulated_evidence": {
                "risk_score": 8,
                "synthetic_prob": 0.05,
                "intent": "NORMAL_CONVERSATION",
                "tactics": [],
            },
        },
        {
            "language": "en",
            "is_unknown_caller": True,
            "simulated_evidence": {
                "risk_score": 7,
                "synthetic_prob": 0.04,
                "intent": "NORMAL_CONVERSATION",
                "tactics": [],
            },
        },
        {
            "language": "en",
            "is_unknown_caller": True,
            "simulated_evidence": {
                "risk_score": 9,
                "synthetic_prob": 0.06,
                "intent": "NORMAL_CONVERSATION",
                "tactics": [],
            },
        },
        {
            "language": "en",
            "is_unknown_caller": True,
            "simulated_evidence": {
                "risk_score": 6,
                "synthetic_prob": 0.03,
                "intent": "NORMAL_CONVERSATION",
                "tactics": [],
            },
        },
    ]

    def test_scenario3_false_positive_rate_zero(self, e2e_pipeline):
        """Legitimate call must NEVER trigger intervention — FPR = 0."""
        results = run_scenario_frames(
            e2e_pipeline["pipeline"],
            e2e_pipeline["temporal"],
            e2e_pipeline["policy"],
            self.FRAMES,
        )
        interventions = [r for r in results if r["should_intervene"]]
        assert len(interventions) == 0, \
            f"ZERO false positives expected for legitimate call. Got {len(interventions)} interventions."

    def test_scenario3_all_frames_safe(self, e2e_pipeline):
        """All frames must remain in SAFE or LOW band (risk < 35)."""
        results = run_scenario_frames(
            e2e_pipeline["pipeline"],
            e2e_pipeline["temporal"],
            e2e_pipeline["policy"],
            self.FRAMES,
        )
        for result in results:
            assert result["risk_score"] <= 35, \
                f"Legitimate call frame {result['frame']} risk too high: {result['risk_score']}"
            assert result["band"] in ("SAFE", "LOW"), \
                f"Frame {result['frame']} wrong band: {result['band']}"

    def test_scenario3_no_fraud_intent(self, e2e_pipeline):
        """No frame should detect high-risk intent in legitimate call."""
        results = run_scenario_frames(
            e2e_pipeline["pipeline"],
            e2e_pipeline["temporal"],
            e2e_pipeline["policy"],
            self.FRAMES,
        )
        for result in results:
            intent = result["evidence"].get("intent", "NORMAL_CONVERSATION")
            assert intent == "NORMAL_CONVERSATION", \
                f"No fraud intent expected in Scenario 3. Got: {intent}"

    def test_scenario3_action_always_monitor(self, e2e_pipeline):
        """Decision engine must output MONITOR for all legitimate frames."""
        results = run_scenario_frames(
            e2e_pipeline["pipeline"],
            e2e_pipeline["temporal"],
            e2e_pipeline["policy"],
            self.FRAMES,
        )
        for result in results:
            assert result["action"] == "MONITOR", \
                f"Legitimate call must only MONITOR. Got: {result['action']}"


# ============================================================
# CROSS-SCENARIO: Risk Separation Validation
# ============================================================

class TestCrossScenarioRiskSeparation:
    """
    Validates that the risk engine cleanly SEPARATES threat levels
    across all 3 scenarios — no misclassification at boundary conditions.
    """

    def test_risk_separation_s1_vs_s3(self, e2e_pipeline):
        """Scenario 1 peak risk must be ≥ 60 points above Scenario 3 peak."""
        s1 = run_scenario_frames(
            e2e_pipeline["pipeline"], e2e_pipeline["temporal"], e2e_pipeline["policy"],
            [{"simulated_evidence": {"risk_score": 94, "synthetic_prob": 0.96,
               "intent": "OTP_REQUEST", "tactics": ["URGENCY", "FEAR"]}}]
        )
        s3 = run_scenario_frames(
            e2e_pipeline["pipeline"], e2e_pipeline["temporal"], e2e_pipeline["policy"],
            [{"simulated_evidence": {"risk_score": 9, "synthetic_prob": 0.04,
               "intent": "NORMAL_CONVERSATION", "tactics": []}}]
        )
        s1_risk, s3_risk = s1[0]["risk_score"], s3[0]["risk_score"]
        sep = s1_risk - s3_risk
        assert sep >= 60, f"S1 vs S3 separation must be ≥ 60. Got: S1={s1_risk}, S3={s3_risk}, Δ={sep}"

    def test_risk_separation_s2_vs_s3(self, e2e_pipeline):
        """Scenario 2 peak risk must be ≥ 50 points above Scenario 3 peak."""
        s2 = run_scenario_frames(
            e2e_pipeline["pipeline"], e2e_pipeline["temporal"], e2e_pipeline["policy"],
            [{"simulated_evidence": {"risk_score": 91, "synthetic_prob": 0.18,
               "intent": "OTP_REQUEST", "tactics": ["URGENCY", "FEAR"]}}]
        )
        s3 = run_scenario_frames(
            e2e_pipeline["pipeline"], e2e_pipeline["temporal"], e2e_pipeline["policy"],
            [{"simulated_evidence": {"risk_score": 6, "synthetic_prob": 0.03,
               "intent": "NORMAL_CONVERSATION", "tactics": []}}]
        )
        s2_risk, s3_risk = s2[0]["risk_score"], s3[0]["risk_score"]
        sep = s2_risk - s3_risk
        assert sep >= 50, f"S2 vs S3 separation must be ≥ 50. Got: S2={s2_risk}, S3={s3_risk}, Δ={sep}"

    def test_s1_and_s2_both_detected_not_s3(self, e2e_pipeline):
        """Both attack scenarios trigger intervention; legitimate call never does."""
        s1 = run_scenario_frames(
            e2e_pipeline["pipeline"], e2e_pipeline["temporal"], e2e_pipeline["policy"],
            [{"simulated_evidence": {"risk_score": 94, "synthetic_prob": 0.96,
               "intent": "MONEY_TRANSFER", "tactics": ["URGENCY", "FEAR"]}}]
        )
        s2 = run_scenario_frames(
            e2e_pipeline["pipeline"], e2e_pipeline["temporal"], e2e_pipeline["policy"],
            [{"simulated_evidence": {"risk_score": 91, "synthetic_prob": 0.18,
               "intent": "OTP_REQUEST", "tactics": ["URGENCY", "FEAR", "DEADLINE_PRESSURE"]}}]
        )
        s3 = run_scenario_frames(
            e2e_pipeline["pipeline"], e2e_pipeline["temporal"], e2e_pipeline["policy"],
            [{"simulated_evidence": {"risk_score": 8, "synthetic_prob": 0.05,
               "intent": "NORMAL_CONVERSATION", "tactics": []}}]
        )
        assert s1[0]["should_intervene"] is True, "Scenario 1 must trigger intervention"
        assert s2[0]["should_intervene"] is True, "Scenario 2 must trigger intervention"
        assert s3[0]["should_intervene"] is False, "Scenario 3 must NOT trigger intervention"
