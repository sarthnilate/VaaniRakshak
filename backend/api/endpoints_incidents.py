import uuid
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.schemas.incidents import IncidentPayload, EvidenceSummary, EvidenceItem
from backend.db.database import get_async_db, Incident

router = APIRouter(prefix="/incidents", tags=["Threat Incidents"])


@router.get("", response_model=List[IncidentPayload])
async def list_incidents(db: AsyncSession = Depends(get_async_db)):
    """Returns all logged high-risk threat incidents for security analysis."""
    result = await db.execute(select(Incident).order_by(Incident.created_at.desc()))
    incidents = result.scalars().all()

    response = []
    for inc in incidents:
        import json
        ev_data = json.loads(inc.evidence_json) if inc.evidence_json else {}
        summary = EvidenceSummary(**ev_data.get("summary", {}))
        items = [EvidenceItem(**item) for item in ev_data.get("items", [])]

        response.append(IncidentPayload(
            incident_id=inc.incident_id,
            session_id=inc.session_id,
            caller_phone=inc.caller_phone,
            peak_risk_score=inc.peak_risk_score,
            risk_band=inc.risk_band,
            evidence_summary=summary,
            evidence_items=items,
            action_taken=inc.action_taken,
            timestamp=inc.created_at
        ))

    return response
