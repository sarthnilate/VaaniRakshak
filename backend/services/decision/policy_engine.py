import logging
from typing import Dict, Any, List, Tuple, Optional
from backend.config import settings
from backend.schemas.risk import EvidenceItem, EvidenceSummary

logger = logging.getLogger("vaanirakshak.decision.policy")


class PolicyDecisionEngine:
    """Configurable security policy decision engine managing risk bands and intervention triggers."""

    def __init__(self):
        self.engine_name = "Deterministic-Policy-Engine-v1"
        logger.info(f"Initialized {self.engine_name} with {settings.INTERVENTION_WINDOW_SEC}s intervention window.")

    def evaluate_policy(
        self,
        risk_score: int,
        evidence_summary: EvidenceSummary,
        is_trusted_contact: bool = False,
        policy_override: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Evaluates dynamic risk score and evidence against active security policy rules."""

        # Apply configurable policy parameters
        intervention_window = policy_override.get("intervention_window_sec", settings.INTERVENTION_WINDOW_SEC) if policy_override else settings.INTERVENTION_WINDOW_SEC
        critical_thresh = policy_override.get("critical_thresh", settings.RISK_THRESHOLD_CRITICAL) if policy_override else settings.RISK_THRESHOLD_CRITICAL
        high_thresh = policy_override.get("high_thresh", settings.RISK_THRESHOLD_HIGH) if policy_override else settings.RISK_THRESHOLD_HIGH
        medium_thresh = policy_override.get("medium_thresh", settings.RISK_THRESHOLD_MEDIUM) if policy_override else settings.RISK_THRESHOLD_MEDIUM
        low_thresh = policy_override.get("low_thresh", settings.RISK_THRESHOLD_LOW) if policy_override else settings.RISK_THRESHOLD_LOW

        # Exemption Rule: Trusted contact with LOW synthetic probability is exempted
        if is_trusted_contact and evidence_summary.synthetic_probability < 0.30:
            effective_score = min(risk_score, 25)
        else:
            effective_score = risk_score

        # Map score to risk band and action
        if effective_score >= critical_thresh:
            band = "CRITICAL"
            action = "INTERVENE_RECOMMENDED"
            should_intervene = True
        elif effective_score >= high_thresh:
            band = "HIGH"
            action = "ALERT_USER"
            should_intervene = False
        elif effective_score >= medium_thresh:
            band = "MEDIUM"
            action = "ALERT_USER"
            should_intervene = False
        elif effective_score >= low_thresh:
            band = "LOW"
            action = "MONITOR"
            should_intervene = False
        else:
            band = "SAFE"
            action = "MONITOR"
            should_intervene = False

        # Build structured evidence list
        evidence_items: List[EvidenceItem] = []

        if evidence_summary.synthetic_probability >= 0.50:
            evidence_items.append(EvidenceItem(
                type="synthetic_voice",
                score=round(evidence_summary.synthetic_probability, 2),
                details=f"Synthetic voice artifact probability: {int(evidence_summary.synthetic_probability * 100)}%"
            ))

        if evidence_summary.speaker_similarity is not None and evidence_summary.speaker_similarity >= 0.70:
            if evidence_summary.synthetic_probability >= 0.50:
                evidence_items.append(EvidenceItem(
                    type="speaker_impersonation",
                    score=round(evidence_summary.speaker_similarity, 2),
                    details=f"Speaker similarity matches trusted contact ({int(evidence_summary.speaker_similarity * 100)}%) but displays synthetic voice features."
                ))
            else:
                evidence_items.append(EvidenceItem(
                    type="speaker_match",
                    score=round(evidence_summary.speaker_similarity, 2),
                    details=f"Speaker biometrics match enrolled trusted profile ({int(evidence_summary.speaker_similarity * 100)}%)."
                ))

        if evidence_summary.detected_intent and evidence_summary.detected_intent != "NORMAL_CONVERSATION":
            evidence_items.append(EvidenceItem(
                type="high_risk_intent",
                score=0.95,
                details=f"Detected high-risk intent: {evidence_summary.detected_intent}"
            ))

        for tactic in evidence_summary.detected_tactics:
            evidence_items.append(EvidenceItem(
                type=f"social_engineering_{tactic.lower()}",
                score=0.90,
                details=f"Psychological manipulation tactic detected: {tactic}"
            ))

        return {
            "effective_risk_score": effective_score,
            "band": band,
            "action": action,
            "should_intervene": should_intervene,
            "intervention_window_sec": intervention_window,
            "evidence_items": evidence_items,
            "engine": self.engine_name
        }


policy_engine = PolicyDecisionEngine()
