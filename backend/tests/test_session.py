import pytest
from backend.schemas.audio import SessionInitPayload
from backend.services.session_service import session_service, determine_action_and_band


def test_determine_action_and_band():
    assert determine_action_and_band(15) == ("SAFE", "MONITOR")
    assert determine_action_and_band(45) == ("LOW", "MONITOR")
    assert determine_action_and_band(65) == ("MEDIUM", "ALERT_USER")
    assert determine_action_and_band(85) == ("HIGH", "ALERT_USER")
    assert determine_action_and_band(94) == ("CRITICAL", "INTERVENE_RECOMMENDED")


@pytest.mark.asyncio
async def test_session_lifecycle():
    # 1. Initialize session
    init_payload = SessionInitPayload(
        caller_phone="+919876543210",
        is_unknown_caller=True
    )
    res = await session_service.start_session(init_payload)
    assert res.session_id.startswith("sess_")
    assert res.status == "ACTIVE"
    assert res.intervention_window_sec == 10

    session_id = res.session_id

    # 2. Simulate risk progression: 32 -> 58 -> 78 -> 94
    scores = [32, 58, 78, 94]
    expected_bands = ["LOW", "LOW", "MEDIUM", "CRITICAL"]

    for seq, (score, expected_band) in enumerate(zip(scores, expected_bands)):
        simulated_evidence = {
            "synthetic_prob": 0.96 if score > 70 else 0.2,
            "speaker_sim": 0.92 if score > 70 else 0.5,
            "intent": "MONEY_TRANSFER" if score > 70 else "NORMAL_CONVERSATION",
            "tactics": ["URGENCY"] if score > 70 else [],
            "risk_score": score
        }
        update = await session_service.update_session_risk(
            session_id=session_id,
            sequence=seq,
            timestamp_ms=seq * 1000,
            raw_evidence_vector=simulated_evidence
        )

        assert update.risk_score == score
        assert update.band == expected_band

    # 3. End session and verify incident creation
    incident = await session_service.end_session(session_id, action_taken="TERMINATED")
    assert incident is not None
    assert incident.session_id == session_id
    assert incident.peak_risk_score == 94
    assert incident.risk_band == "CRITICAL"
    assert incident.action_taken == "TERMINATED"
