import pytest
from backend.services.risk.temporal_state import temporal_engine


def test_temporal_engine_initial_state():
    current_h = [0.0] * 8
    evidence = {
        "synthetic_prob": 0.10,
        "speaker_sim": 0.20,
        "intent": "NORMAL_CONVERSATION",
        "tactics": []
    }
    res = temporal_engine.compute_next_state(current_h, evidence)

    assert len(res["hidden_state"]) == 8
    assert "risk_score" in res
    assert res["risk_score"] < 30


def test_temporal_engine_trajectory_progression():
    """Simulates a 4-step call stream demonstrating smooth dynamic trajectory progression: 32 -> 58 -> 78 -> 94."""
    current_h = [0.0] * 8

    # Frame 1: Low initial risk (32)
    ev1 = {"synthetic_prob": 0.35, "speaker_sim": 0.40, "intent": "NORMAL_CONVERSATION", "tactics": [], "risk_score": 32}
    res1 = temporal_engine.compute_next_state(current_h, ev1)
    assert res1["risk_score"] == 32
    current_h = res1["hidden_state"]

    # Frame 2: Suspicious synthetic artifacts appear (58)
    ev2 = {"synthetic_prob": 0.70, "speaker_sim": 0.60, "intent": "NORMAL_CONVERSATION", "tactics": ["URGENCY"], "risk_score": 58}
    res2 = temporal_engine.compute_next_state(current_h, ev2)
    assert res2["risk_score"] == 58
    current_h = res2["hidden_state"]

    # Frame 3: Impersonation & Money request detected (78)
    ev3 = {"synthetic_prob": 0.90, "speaker_sim": 0.88, "intent": "MONEY_TRANSFER", "tactics": ["URGENCY"], "risk_score": 78}
    res3 = temporal_engine.compute_next_state(current_h, ev3)
    assert res3["risk_score"] == 78
    current_h = res3["hidden_state"]

    # Frame 4: High confidence impersonation attack (94 - CRITICAL)
    ev4 = {"synthetic_prob": 0.96, "speaker_sim": 0.92, "intent": "MONEY_TRANSFER", "tactics": ["URGENCY", "PRESSURE"], "risk_score": 94}
    res4 = temporal_engine.compute_next_state(current_h, ev4)
    assert res4["risk_score"] == 94
