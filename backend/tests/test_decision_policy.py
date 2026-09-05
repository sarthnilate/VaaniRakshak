import pytest
from backend.services.decision.policy_engine import policy_engine
from backend.schemas.risk import EvidenceSummary


def test_policy_engine_safe_evaluation():
    summary = EvidenceSummary(
        synthetic_probability=0.05,
        human_probability=0.95,
        speaker_similarity=0.94,
        detected_intent="NORMAL_CONVERSATION"
    )
    res = policy_engine.evaluate_policy(risk_score=12, evidence_summary=summary)

    assert res["band"] == "SAFE"
    assert res["action"] == "MONITOR"
    assert res["should_intervene"] is False
    assert res["intervention_window_sec"] == 10


def test_policy_engine_critical_intervention_trigger():
    summary = EvidenceSummary(
        synthetic_probability=0.96,
        human_probability=0.04,
        speaker_similarity=0.92,
        detected_intent="MONEY_TRANSFER",
        detected_tactics=["URGENCY"]
    )
    res = policy_engine.evaluate_policy(risk_score=94, evidence_summary=summary)

    assert res["band"] == "CRITICAL"
    assert res["action"] == "INTERVENE_RECOMMENDED"
    assert res["should_intervene"] is True
    assert res["intervention_window_sec"] == 10
    assert len(res["evidence_items"]) >= 3


def test_policy_engine_trusted_contact_exemption():
    summary = EvidenceSummary(
        synthetic_probability=0.10,  # Low synthetic score
        speaker_similarity=0.95,
        detected_intent="NORMAL_CONVERSATION"
    )
    # Trusted contact with low synth score should be exempted to SAFE
    res = policy_engine.evaluate_policy(risk_score=65, evidence_summary=summary, is_trusted_contact=True)
    assert res["band"] == "SAFE"
    assert res["should_intervene"] is False
