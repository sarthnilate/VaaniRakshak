import hashlib
import json
import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger("vaanirakshak.attack_lab.provenance")


class ProvenanceTracker:
    """Manages cryptographic provenance tracking and metadata watermarking for Attack Lab audio."""

    def create_provenance(
        self,
        sample_id: str,
        generator_family: str,
        prompt: str,
        reference_speaker_id: str,
        consent_token: str = "CONSENT_RESEARCH_APPROVED"
    ) -> Dict[str, Any]:
        """Creates cryptographic provenance metadata payload."""
        timestamp = datetime.utcnow().isoformat()
        raw_token = f"{sample_id}:{generator_family}:{reference_speaker_id}:{consent_token}:{timestamp}"
        consent_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

        provenance = {
            "sample_id": sample_id,
            "is_synthetic": True,
            "generator_family": generator_family,
            "reference_speaker_id": reference_speaker_id,
            "prompt_snippet": prompt[:50],
            "consent_token": consent_token,
            "consent_hash": consent_hash,
            "timestamp": timestamp,
            "watermark_tag": "VAANIRAKSHAK_ATTACK_LAB_RESEARCH_SYNTHETIC"
        }
        logger.info(f"Created provenance metadata for sample {sample_id} (Hash: {consent_hash[:10]})")
        return provenance

    def verify_provenance(self, provenance: Dict[str, Any]) -> bool:
        """Verifies provenance metadata payload validity."""
        if not provenance:
            return False
        if not provenance.get("is_synthetic"):
            return False
        if provenance.get("watermark_tag") != "VAANIRAKSHAK_ATTACK_LAB_RESEARCH_SYNTHETIC":
            return False
        if not provenance.get("consent_hash"):
            return False
        return True


provenance_tracker = ProvenanceTracker()
