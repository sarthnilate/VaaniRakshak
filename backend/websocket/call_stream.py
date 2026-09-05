import json
import logging
from typing import Dict
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.schemas.audio import AudioChunkPayload
from backend.services.session_service import session_service

logger = logging.getLogger("vaanirakshak.websocket")

router = APIRouter()


class ConnectionManager:
    """Manages active WebSocket connections per call session."""

    def __init__(self):
        self.active_connections: Dict[str, list[WebSocket]] = {}

    async def connect(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        self.active_connections[session_id].append(websocket)
        logger.info(f"WebSocket client connected to session {session_id}")

    def disconnect(self, session_id: str, websocket: WebSocket):
        if session_id in self.active_connections:
            if websocket in self.active_connections[session_id]:
                self.active_connections[session_id].remove(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
        logger.info(f"WebSocket client disconnected from session {session_id}")

    async def broadcast_to_session(self, session_id: str, message: dict):
        if session_id in self.active_connections:
            for connection in self.active_connections[session_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting WS message to session {session_id}: {e}")


ws_manager = ConnectionManager()


@router.websocket("/ws/call/{session_id}")
async def websocket_call_stream(websocket: WebSocket, session_id: str):
    """Streaming WebSocket endpoint receiving real-time PCM audio chunks and broadcasting risk updates."""
    await ws_manager.connect(session_id, websocket)

    try:
        while True:
            raw_text = await websocket.receive_text()
            data = json.loads(raw_text)
            msg_type = data.get("type", "audio_chunk")

            if msg_type == "audio_chunk":
                chunk_payload = AudioChunkPayload(**data)

                # Process chunk through session service & AI pipeline
                risk_update = await session_service.update_session_risk(
                    session_id=session_id,
                    sequence=chunk_payload.sequence,
                    timestamp_ms=chunk_payload.timestamp_ms,
                    pcm_b64=chunk_payload.pcm_b64,
                    raw_evidence_vector=data.get("simulated_evidence")  # Accepts simulated vector if provided during testing
                )

                # Broadcast risk update back to all session subscribers (App + Dashboard)
                await ws_manager.broadcast_to_session(session_id, risk_update.model_dump(mode="json"))

            elif msg_type == "heartbeat":
                await websocket.send_json({"type": "heartbeat_ack", "session_id": session_id})

            elif msg_type == "close_session":
                action_taken = data.get("action_taken", "COMPLETED")
                incident = await session_service.end_session(session_id, action_taken=action_taken)
                response = {"type": "session_closed", "session_id": session_id}
                if incident:
                    response["incident"] = incident.model_dump(mode="json")
                await websocket.send_json(response)
                break

    except WebSocketDisconnect:
        logger.info(f"Client disconnected from WS session {session_id}")
        ws_manager.disconnect(session_id, websocket)
    except Exception as e:
        logger.error(f"WebSocket error on session {session_id}: {e}")
        ws_manager.disconnect(session_id, websocket)
        try:
            await websocket.close()
        except Exception:
            pass
