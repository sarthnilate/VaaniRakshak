import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.schemas.audio import SessionInitPayload
from backend.services.session_service import session_service


@pytest.mark.asyncio
async def test_websocket_streaming():
    # Start session first
    init_res = await session_service.start_session(SessionInitPayload(caller_phone="+919876543210"))
    session_id = init_res.session_id

    client = TestClient(app)
    with client.websocket_connect(f"/ws/call/{session_id}") as websocket:
        # Send heartbeat
        websocket.send_json({"type": "heartbeat"})
        ack = websocket.receive_json()
        assert ack["type"] == "heartbeat_ack"
        assert ack["session_id"] == session_id

        # Send audio chunk with simulated evidence
        chunk_data = {
            "type": "audio_chunk",
            "sequence": 1,
            "timestamp_ms": 1000,
            "pcm_b64": "c2FtcGxlcGNtZGF0YQ==",
            "simulated_evidence": {
                "synthetic_prob": 0.96,
                "speaker_sim": 0.92,
                "intent": "MONEY_TRANSFER",
                "tactics": ["URGENCY"],
                "risk_score": 94
            }
        }
        websocket.send_json(chunk_data)

        # Receive risk update
        risk_res = websocket.receive_json()
        assert risk_res["type"] == "risk_update"
        assert risk_res["session_id"] == session_id
        assert risk_res["risk_score"] == 94
        assert risk_res["band"] == "CRITICAL"
        assert risk_res["action"] == "INTERVENE_RECOMMENDED"
        assert risk_res["policy_window_sec"] == 10

        # Send close_session
        websocket.send_json({"type": "close_session", "action_taken": "TERMINATED"})
        close_res = websocket.receive_json()
        assert close_res["type"] == "session_closed"
        assert close_res["session_id"] == session_id
        assert close_res["incident"]["peak_risk_score"] == 94
