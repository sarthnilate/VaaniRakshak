from fastapi import APIRouter, HTTPException, status
from backend.schemas.audio import SessionInitPayload, SessionInitResponse
from backend.schemas.incidents import IncidentPayload
from backend.services.session_service import session_service
from backend.db.redis import session_manager

router = APIRouter(prefix="/sessions", tags=["Call Sessions"])


@router.post("/start", response_model=SessionInitResponse, status_code=status.HTTP_201_CREATED)
async def start_call_session(payload: SessionInitPayload):
    """Initializes a new protected call session."""
    try:
        return await session_service.start_session(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}")
async def get_session_status(session_id: str):
    """Returns current session metadata and risk status."""
    session = await session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or expired.")
    history = await session_manager.get_risk_history(session_id)
    return {
        "session": session,
        "history": history
    }


@router.post("/{session_id}/end", response_model=dict)
async def end_call_session(session_id: str, action_taken: str = "COMPLETED"):
    """Ends active call session and generates incident report if risk escalated."""
    incident = await session_service.end_session(session_id, action_taken=action_taken)
    return {
        "session_id": session_id,
        "status": "TERMINATED",
        "incident": incident.model_dump() if incident else None
    }
