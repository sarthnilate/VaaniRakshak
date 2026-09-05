import uuid
import logging
from datetime import datetime
from typing import Tuple, List, Optional

from backend.config import settings
from backend.schemas.audio import SessionInitPayload, SessionInitResponse
from backend.schemas.risk import RiskUpdatePayload, EvidenceSummary, EvidenceItem
from backend.schemas.incidents import IncidentPayload
from backend.db.redis import session_manager
from backend.services.ai.pipeline_aggregator import ai_pipeline
from backend.services.risk.temporal_state import temporal_engine
from backend.services.decision.policy_engine import policy_engine

logger = logging.getLogger("vaanirakshak.session_service")


def determine_action_and_band(score: int) -> Tuple[str, str]:
    """Determines risk band and recommended system action based on configurable threshold settings."""
    if score >= settings.RISK_THRESHOLD_CRITICAL:
        return "CRITICAL", "INTERVENE_RECOMMENDED"
    elif score >= settings.RISK_THRESHOLD_HIGH:
        return "HIGH", "ALERT_USER"
    elif score >= settings.RISK_THRESHOLD_MEDIUM:
        return "MEDIUM", "ALERT_USER"
    elif score >= settings.RISK_THRESHOLD_LOW:
        return "LOW", "MONITOR"
    else:
        return "SAFE", "MONITOR"


class SessionService:
    """Manages live call sessions, evidence accumulation, temporal risk GRU state, and policy decisions."""

    async def start_session(self, init_payload: SessionInitPayload) -> SessionInitResponse:
        session_id = f"sess_{uuid.uuid4().hex[:12]}"
        metadata = {
            "session_id": session_id,
            "caller_phone": init_payload.caller_phone,
            "is_unknown_caller": init_payload.is_unknown_caller,
            "protected_contact_id": init_payload.protected_contact_id,
            "language": init_payload.language,
            "status": "ACTIVE",
            "current_risk_score": 0,
            "current_band": "SAFE",
            "hidden_state": [0.0] * 8,
            "created_at": datetime.utcnow().isoformat()
        }

        await session_manager.create_session(session_id, metadata, ttl_sec=settings.REDIS_SESSION_TTL_SEC)
        logger.info(f"Initialized call session {session_id} for caller {init_payload.caller_phone}")

        return SessionInitResponse(
            session_id=session_id,
            status="ACTIVE",
            created_at=datetime.utcnow(),
            intervention_window_sec=settings.INTERVENTION_WINDOW_SEC,
            critical_threshold=settings.RISK_THRESHOLD_CRITICAL
        )

    async def update_session_risk(
        self,
        session_id: str,
        sequence: int,
        timestamp_ms: int,
        pcm_b64: str = "",
        raw_evidence_vector: Optional[dict] = None
    ) -> RiskUpdatePayload:
        session = await session_manager.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found or expired.")

        # 1. Run AI Multi-Evidence Pipeline
        preferred_language = session.get("language", "en")
        evidence_vector = ai_pipeline.process_chunk(
            pcm_b64=pcm_b64,
            preferred_language=preferred_language,
            simulated_evidence=raw_evidence_vector
        )

        # 2. Run Temporal Risk State Engine (GRU recurrence)
        is_unknown = session.get("is_unknown_caller", True)
        current_hidden_state = session.get("hidden_state", [0.0] * 8)
        
        temporal_res = temporal_engine.compute_next_state(
            current_state=current_hidden_state,
            evidence_vector=evidence_vector,
            is_unknown_caller=is_unknown
        )

        computed_score = temporal_res["risk_score"]
        session["hidden_state"] = temporal_res["hidden_state"]

        # 3. Run Policy Decision Engine
        summary = EvidenceSummary(
            synthetic_probability=evidence_vector.get("synthetic_prob", 0.05),
            human_probability=evidence_vector.get("human_prob", 0.95),
            speaker_similarity=evidence_vector.get("speaker_sim"),
            detected_intent=evidence_vector.get("intent", "NORMAL_CONVERSATION"),
            detected_tactics=evidence_vector.get("tactics", []),
            transcript_snippet=evidence_vector.get("transcript", "")
        )

        is_trusted = not is_unknown or session.get("protected_contact_id") is not None
        policy_res = policy_engine.evaluate_policy(
            risk_score=computed_score,
            evidence_summary=summary,
            is_trusted_contact=is_trusted
        )

        update_payload = RiskUpdatePayload(
            type="risk_update",
            session_id=session_id,
            sequence=sequence,
            timestamp_ms=timestamp_ms,
            risk_score=policy_res["effective_risk_score"],
            band=policy_res["band"],
            action=policy_res["action"],
            evidence_summary=summary,
            evidence=policy_res["evidence_items"],
            policy_window_sec=policy_res["intervention_window_sec"]
        )

        # Store risk update in session history
        await session_manager.record_risk_update(session_id, update_payload.model_dump(mode="json"))
        return update_payload

    async def end_session(self, session_id: str, action_taken: str = "COMPLETED") -> Optional[IncidentPayload]:
        session = await session_manager.get_session(session_id)
        if not session:
            return None

        history = await session_manager.get_risk_history(session_id)
        peak_score = max([rec.get("risk_score", 0) for rec in history], default=session.get("current_risk_score", 0))
        peak_band, _ = determine_action_and_band(peak_score)

        last_update = history[-1] if history else {}
        summary_dict = last_update.get("evidence_summary", {})
        evidence_summary = EvidenceSummary(**summary_dict) if summary_dict else EvidenceSummary()

        incident = IncidentPayload(
            incident_id=f"inc_{uuid.uuid4().hex[:10]}",
            session_id=session_id,
            caller_phone=session.get("caller_phone", "UNKNOWN"),
            peak_risk_score=peak_score,
            risk_band=peak_band,
            evidence_summary=evidence_summary,
            evidence_items=[EvidenceItem(**item) for item in last_update.get("evidence", [])],
            action_taken=action_taken,
            timestamp=datetime.utcnow()
        )

        await session_manager.close_session(session_id)
        logger.info(f"Closed session {session_id}. Peak Risk: {peak_score} ({peak_band}). Action: {action_taken}")
        return incident


session_service = SessionService()
