import logging
from typing import Dict, Any, List, Optional

from backend.services.ai.voice_authenticity import authenticity_engine
from backend.services.ai.speaker_verification import speaker_engine
from backend.services.ai.stt_engine import stt_engine
from backend.services.ai.intent_nlp import intent_engine

logger = logging.getLogger("vaanirakshak.ai.pipeline")


class MultiEvidencePipeline:
    """Aggregates all 4 AI evidence extraction engines (Authenticity, Biometrics, STT, Intent/Tactics NLP)."""

    def process_chunk(
        self,
        pcm_b64: str,
        enrolled_speaker_embeddings: Optional[List[List[float]]] = None,
        preferred_language: str = "en",
        simulated_evidence: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Runs parallel feature extraction across physical, biometric, linguistic, and psychological threat vectors."""

        # 1. Voice Authenticity (Anti-Spoofing) Engine
        auth_res = authenticity_engine.analyze_audio_chunk(pcm_b64, simulated_override=simulated_evidence)

        # 2. Speaker Verification (Biometrics) Engine
        speaker_res = speaker_engine.verify_speaker(
            pcm_b64,
            enrolled_embeddings=enrolled_speaker_embeddings or [],
            simulated_override=simulated_evidence
        )

        # 3. Speech-to-Text (STT) Engine
        stt_res = stt_engine.transcribe_chunk(
            pcm_b64,
            preferred_language=preferred_language,
            simulated_override=simulated_evidence
        )

        # 4. Conversation Intelligence & Social Engineering NLP Engine
        transcript_text = stt_res.get("transcription", "")
        intent_res = intent_engine.analyze_transcript(transcript_text, simulated_override=simulated_evidence)

        # Combine into unified multi-evidence output vector
        raw_vector = {
            "synthetic_prob": auth_res["synthetic_probability"],
            "human_prob": auth_res["human_probability"],
            "speaker_sim": speaker_res["speaker_similarity"],
            "is_enrolled_match": speaker_res["is_enrolled_match"],
            "transcript": transcript_text,
            "detected_language": stt_res["detected_language"],
            "intent": intent_res["detected_intent"],
            "tactics": intent_res["detected_tactics"],
            "is_high_risk": intent_res["is_high_risk"],
            "evidence_details": {
                "authenticity": auth_res,
                "biometrics": speaker_res,
                "stt": stt_res,
                "nlp": intent_res
            }
        }

        if simulated_evidence and "risk_score" in simulated_evidence:
            raw_vector["risk_score"] = simulated_evidence["risk_score"]

        return raw_vector


ai_pipeline = MultiEvidencePipeline()
