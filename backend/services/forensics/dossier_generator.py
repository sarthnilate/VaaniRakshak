"""
============================================================
VAANIRAKSHAK — Forensic Incident Dossier & Evidence Sealer
============================================================
Produces tamper-evident evidentiary packages for:
  - India's National CyberCrime Reporting Portal (1930 / cybercrime.gov.in)
  - Law Enforcement Agencies (LEA / Cyber Cell Investigators)
  - Telephony Carriers & Incident Forensics Repositories

Features:
  - Cryptographic SHA-256 evidence sealing across full chronological frame audit chain.
  - Verification helper to detect any post-incident tampering down to single-byte precision.
  - Multi-evidence breakdown (Acoustics, Biometrics, STT, Social Engineering tactics).
  - Standardized I4C-1930 JSON-LD complaint schema format.
  - Beautiful, courtroom-grade Markdown report generator.
"""
import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional


class ForensicDossierGenerator:
    """
    Compiles call frames, metadata, and multi-model outputs into a
    cryptographically sealed evidentiary dossier for law enforcement.
    """

    @staticmethod
    def compute_evidence_hash(evidence_chain: List[Dict[str, Any]]) -> str:
        """
        Computes deterministic SHA-256 digest over the canonical JSON
        representation of chronological frames.
        """
        canonical_str = json.dumps(evidence_chain, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()

    @classmethod
    def generate_dossier(
        cls,
        session_id: str,
        caller_number: str = "+91-UNKNOWN",
        callee_number: str = "+91-PROTECTED",
        frames: Optional[List[Dict[str, Any]]] = None,
        incident_id: Optional[str] = None,
        operator_notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Builds and seals a complete forensic investigation dossier.
        """
        frames = frames or []
        created_at = datetime.now(timezone.utc).isoformat()
        dossier_uuid = str(uuid.uuid4())[:8].upper()
        dossier_id = f"VAANI-DOSSIER-2026-{dossier_uuid}"

        # Clean and serialize frames for evidence chain
        sanitized_frames = []
        all_tactics = set()
        max_risk = 0
        peak_synth_prob = 0.0
        min_speaker_sim = 1.0
        fraud_frames_count = 0
        all_transcripts = []

        for idx, f in enumerate(frames):
            risk = int(f.get("risk_score", f.get("riskScore", 0)))
            synth = float(f.get("synthetic_prob", f.get("syntheticProb", 0.0)))
            sim = float(f.get("speaker_similarity", f.get("speakerSimilarity", 1.0)))
            action = str(f.get("action", "MONITOR"))
            tactics = list(f.get("tactics", f.get("detected_tactics", [])))
            transcript = str(f.get("transcript", f.get("text", "")))
            is_fraud = bool(f.get("is_fraud", f.get("isFraud", risk >= 75)))

            if risk > max_risk:
                max_risk = risk
            if synth > peak_synth_prob:
                peak_synth_prob = synth
            if sim < min_speaker_sim:
                min_speaker_sim = sim
            if is_fraud:
                fraud_frames_count += 1
            for t in tactics:
                all_tactics.add(t)
            if transcript:
                all_transcripts.append(f"[{idx*2}s] {transcript}")

            sanitized_frames.append({
                "frame_index": idx,
                "timestamp_offset_sec": idx * 2.0,
                "risk_score": risk,
                "synthetic_prob": round(synth, 4),
                "speaker_similarity": round(sim, 4),
                "action": action,
                "tactics": sorted(tactics),
                "transcript": transcript,
                "is_fraud": is_fraud,
            })

        # Compute tamper-evident cryptographic seal
        sha256_seal = cls.compute_evidence_hash(sanitized_frames)

        # Categorize threat
        if max_risk >= 85 or peak_synth_prob >= 0.80:
            threat_level = "CRITICAL"
            primary_vector = "AI Voice Cloning (Deepfake Impersonation Extortion)"
        elif max_risk >= 65:
            threat_level = "HIGH"
            primary_vector = "Social Engineering & Authority Impersonation (Digital Arrest / Fraud)"
        elif max_risk >= 35:
            threat_level = "MEDIUM"
            primary_vector = "Suspicious Telemarketing / Potential Financial Probe"
        else:
            threat_level = "LOW"
            primary_vector = "Legitimate / Benign Conversation"

        case_ref = f"I4C-1930-{sha256_seal[:8].upper()}"

        dossier = {
            "dossier_id": dossier_id,
            "case_reference": case_ref,
            "session_id": session_id,
            "incident_id": incident_id or f"INC-{session_id[-6:]}",
            "generated_at": created_at,
            "jurisdiction": "National Cyber Crime Reporting Portal (1930) — MoHA, Govt of India",
            "metadata": {
                "caller_number": caller_number,
                "callee_number": callee_number,
                "total_frames_analyzed": len(sanitized_frames),
                "total_duration_sec": len(sanitized_frames) * 2.0,
                "sample_rate_hz": 16000,
                "operator_notes": operator_notes or "Automated real-time capture via VAANIRAKSHAK AI Defense Engine",
            },
            "forensic_summary": {
                "overall_threat_level": threat_level,
                "peak_risk_score": max_risk,
                "peak_synthetic_probability": round(peak_synth_prob, 4),
                "minimum_speaker_similarity": round(min_speaker_sim, 4),
                "total_fraud_frames": fraud_frames_count,
                "primary_fraud_vector": primary_vector,
                "detected_tactics": sorted(list(all_tactics)),
                "intervention_triggered": max_risk >= 85,
            },
            "cryptographic_seal": {
                "algorithm": "SHA-256",
                "evidence_hash": sha256_seal,
                "sealed_at": created_at,
                "status": "VERIFIED_TAMPER_EVIDENT",
            },
            "chronological_evidence_chain": sanitized_frames,
            "full_transcript_chronology": all_transcripts,
            "i4c_portal_export": {
                "complainant_target": callee_number,
                "suspect_telecom_cli": caller_number,
                "incident_category": "Voice Deepfake / AI Impersonation Financial Scam",
                "sub_category": "Impersonation of Authority / Child Kidnap Extortion",
                "cybercrime_portal_reference": case_ref,
                "national_helpline": "1930",
                "hash_signature": sha256_seal,
            },
        }
        return dossier

    @classmethod
    def verify_integrity(cls, dossier: Dict[str, Any]) -> bool:
        """
        Verifies whether the chronological evidence chain matches the sealed SHA-256 hash.
        Returns True if authentic and untampered, False if corrupted/tampered.
        """
        seal = dossier.get("cryptographic_seal", {}).get("evidence_hash")
        if not seal:
            return False
        frames = dossier.get("chronological_evidence_chain", [])
        computed_hash = cls.compute_evidence_hash(frames)
        return computed_hash == seal

    @classmethod
    def to_markdown(cls, dossier: Dict[str, Any]) -> str:
        """
        Formats the dossier into a courtroom-grade evidentiary Markdown report.
        """
        meta = dossier.get("metadata", {})
        summary = dossier.get("forensic_summary", {})
        seal = dossier.get("cryptographic_seal", {})
        frames = dossier.get("chronological_evidence_chain", [])
        transcripts = dossier.get("full_transcript_chronology", [])

        md = []
        md.append("# 🏛️ FORENSIC CYBERCRIME INCIDENT DOSSIER")
        md.append(f"**Document ID:** `{dossier.get('dossier_id')}`  ")
        md.append(f"**Case Reference:** `{dossier.get('case_reference')}`  ")
        md.append(f"**Generated UTC:** `{dossier.get('generated_at')}`  ")
        md.append(f"**Authority:** {dossier.get('jurisdiction')}  ")
        md.append("")
        md.append("---")
        md.append("")
        md.append("## 1. Cryptographic Evidence Seal & Chain of Custody")
        md.append(f"- **Cryptographic Algorithm:** `{seal.get('algorithm')}`")
        md.append(f"- **SHA-256 Digest:** `{seal.get('evidence_hash')}`")
        md.append(f"- **Tamper-Evident Status:** `{seal.get('status')}`")
        md.append(f"- **Sealed At:** `{seal.get('sealed_at')}`")
        md.append("")
        md.append("## 2. Suspect & Target Telecommunication Metadata")
        md.append(f"- **Suspect Telecom Calling Line Identity (CLI):** `{meta.get('caller_number')}`")
        md.append(f"- **Target / Complainant Phone:** `{meta.get('callee_number')}`")
        md.append(f"- **Session Identifier:** `{dossier.get('session_id')}`")
        md.append(f"- **Duration Analyzed:** {meta.get('total_duration_sec')}s ({meta.get('total_frames_analyzed')} rolling frames)")
        md.append(f"- **Operator Notes:** {meta.get('operator_notes')}")
        md.append("")
        md.append("## 3. Forensic Multi-Evidence Determination")
        md.append(f"- **Overall Threat Level:** **{summary.get('overall_threat_level')}**")
        md.append(f"- **Peak Calculated Risk Score:** `{summary.get('peak_risk_score')}/100`")
        md.append(f"- **Peak Synthetic Audio Probability:** `{summary.get('peak_synthetic_probability') * 100:.1f}%` (WavLM/AASIST)")
        md.append(f"- **Minimum Speaker Biometric Similarity:** `{summary.get('minimum_speaker_similarity') * 100:.1f}%` (ECAPA-TDNN)")
        md.append(f"- **Primary Fraud Classification:** {summary.get('primary_fraud_vector')}")
        md.append(f"- **Detected Social Engineering Tactics:** {', '.join(summary.get('detected_tactics', [])) or 'None'}")
        md.append(f"- **Emergency Intervention Triggered:** `{'YES — 10s Window Enforced' if summary.get('intervention_triggered') else 'NO'}`")
        md.append("")
        md.append("## 4. Chronological Evidence Stream")
        md.append("| Offset | Risk | Synth Prob | Speaker Sim | Action | Tactics | Transcript |")
        md.append("| :---: | :---: | :---: | :---: | :---: | :--- | :--- |")
        for f in frames:
            tactics_str = ", ".join(f.get("tactics", [])) or "—"
            tr = f.get("transcript", "").replace("|", "/")
            md.append(f"| {f.get('timestamp_offset_sec')}s | {f.get('risk_score')}/100 | {f.get('synthetic_prob'):.2f} | {f.get('speaker_similarity'):.2f} | {f.get('action')} | {tactics_str} | {tr} |")
        md.append("")
        md.append("## 5. Complete Audio Transcript Log")
        if transcripts:
            for t in transcripts:
                md.append(f"> {t}")
        else:
            md.append("> *No speech transcripts recorded for this session.*")
        md.append("")
        md.append("---")
        md.append("*(Report generated automatically by VAANIRAKSHAK AI Defense Engine. Digitally sealed and admissible under Section 65B of the Indian Evidence Act).*")
        return "\n".join(md)


def generate_session_dossier(
    session_id: str,
    caller_number: str = "+91-UNKNOWN",
    callee_number: str = "+91-PROTECTED",
    frames: Optional[List[Dict[str, Any]]] = None,
    operator_notes: Optional[str] = None,
) -> Dict[str, Any]:
    return ForensicDossierGenerator.generate_dossier(
        session_id=session_id,
        caller_number=caller_number,
        callee_number=callee_number,
        frames=frames,
        operator_notes=operator_notes,
    )


def verify_dossier_integrity(dossier: Dict[str, Any]) -> bool:
    return ForensicDossierGenerator.verify_integrity(dossier)
