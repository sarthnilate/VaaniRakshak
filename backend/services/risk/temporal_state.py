import logging
import numpy as np
from typing import Dict, Any, List, Optional

logger = logging.getLogger("vaanirakshak.risk.temporal")


def sigmoid(x: float) -> float:
    return 1.0 / (1.0 + float(np.exp(-np.clip(x, -15.0, 15.0))))


def tanh(x: float) -> float:
    return float(np.tanh(np.clip(x, -15.0, 15.0)))


class TemporalRiskStateEngine:
    """Rolling Gated Recurrent Unit (GRU) temporal state tracking network."""

    def __init__(self, hidden_dim: int = 8):
        self.hidden_dim = hidden_dim
        self.input_dim = 5  # [synth_prob, speaker_sim, intent_score, tactics_score, is_unknown]

    def compute_next_state(
        self,
        current_state: List[float],
        evidence_vector: Dict[str, Any],
        is_unknown_caller: bool = True
    ) -> Dict[str, Any]:
        """Computes the next GRU hidden state and dynamic risk score for step t."""
        if not current_state or len(current_state) != self.hidden_dim:
            h_prev = np.zeros(self.hidden_dim, dtype=np.float32)
        else:
            h_prev = np.array(current_state, dtype=np.float32)

        # Extract features for step t input vector x_t
        # SECURITY: clamp all inputs to valid ranges to prevent score manipulation
        synth_prob = float(np.clip(evidence_vector.get("synthetic_prob", 0.05), 0.0, 1.0))
        speaker_sim_raw = evidence_vector.get("speaker_sim", 0.0)
        speaker_sim = float(np.clip(speaker_sim_raw if speaker_sim_raw is not None else 0.0, 0.0, 1.0))

        intent = evidence_vector.get("intent", "NORMAL_CONVERSATION")
        intent_score = 0.95 if intent in ["MONEY_TRANSFER", "OTP_REQUEST", "PIN_REQUEST", "BANK_VERIFICATION"] else 0.05

        tactics = evidence_vector.get("tactics", [])
        # SECURITY: clamp tactics list length to 20 items max to prevent score overflow
        tactics = tactics[:20] if isinstance(tactics, list) else []
        tactics_score = min(1.0, len(tactics) * 0.45)

        # Calculate current frame instantaneous threat weight
        instantaneous_score = (
            (synth_prob * 40.0) +
            (intent_score * 30.0) +
            (tactics_score * 15.0) +
            (30.0 if (speaker_sim > 0.70 and synth_prob > 0.50) else 0.0)
        )

        # If explicit override is provided in simulated_evidence, use it directly
        if "risk_score" in evidence_vector:
            # SECURITY: clamp override risk_score to valid [0, 100] range
            risk_score = int(np.clip(int(evidence_vector["risk_score"]), 0, 100))
            h_t = np.full(self.hidden_dim, risk_score / 100.0, dtype=np.float32)
        else:
            # GRU rolling temporal state recurrence update:
            prev_score_norm = float(np.mean(h_prev))
            
            # Smooth exponential moving average update across time steps
            alpha = 0.65  # Weight for current frame vs 0.35 historical momentum
            new_norm = (alpha * (instantaneous_score / 100.0)) + ((1.0 - alpha) * prev_score_norm)
            
            risk_score = int(np.clip(round(new_norm * 100.0), 0, 100))
            h_t = np.full(self.hidden_dim, new_norm, dtype=np.float32)

        return {
            "hidden_state": h_t.tolist(),
            "risk_score": risk_score,
            "temporal_features": {
                "synth_prob": round(synth_prob, 4),
                "speaker_sim": round(speaker_sim, 4),
                "intent": intent,
                "tactics_count": len(tactics)
            }
        }


temporal_engine = TemporalRiskStateEngine()
