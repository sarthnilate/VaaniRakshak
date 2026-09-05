"""
============================================================
VAANIRAKSHAK — Forensics & Carrier Webhook Endpoints
============================================================
Exposes REST endpoints for:
  - Cryptographic forensic dossier generation & tamper verification
  - Markdown/JSON evidentiary package export for CyberCrime (1930)
  - Telecom carrier CDR & SIP trunk call control webhooks
"""
from fastapi import APIRouter, HTTPException, Query, Response
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import json

from backend.services.forensics.dossier_generator import (
    ForensicDossierGenerator,
    generate_session_dossier,
    verify_dossier_integrity,
)
from backend.services.carrier.sip_trunk_adapter import (
    CarrierSipTrunkAdapter,
)

router = APIRouter(prefix="/forensics", tags=["Forensics & CyberCrime 1930"])
carrier_router = APIRouter(prefix="/carrier", tags=["Carrier Telephony Webhooks"])

# In-memory dossier archive for demo
_DOSSIER_STORE: Dict[str, Dict[str, Any]] = {}
carrier_adapter = CarrierSipTrunkAdapter()


class DossierGenerateRequest(BaseModel):
    session_id: str = Field(..., description="Unique call session ID")
    caller_number: str = Field(default="+91-UNKNOWN", description="Suspect phone number")
    callee_number: str = Field(default="+91-PROTECTED", description="Victim/Target phone number")
    frames: List[Dict[str, Any]] = Field(default_factory=list, description="Chronological call frames")
    operator_notes: Optional[str] = Field(default=None, description="Investigator notes")


class CarrierEventRequest(BaseModel):
    call_id: str
    calling_party: str
    called_party: str
    sip_method: Optional[str] = "INVITE"
    codec: Optional[str] = "AMR-WB/16000"
    cell_tower_cgi: Optional[str] = "404-45-8192-3021"
    packet_loss_pct: Optional[float] = 0.5
    jitter_ms: Optional[float] = 3.2


class CarrierTeardownRequest(BaseModel):
    call_id: str
    reason: Optional[str] = "AI_VOICE_FRAUD_INTERVENTION"


@router.post("/dossier/generate", summary="Generate & Cryptographically Seal Forensic Dossier")
async def generate_dossier_endpoint(req: DossierGenerateRequest):
    """
    Creates an evidentiary dossier with SHA-256 seal across all chronological frames.
    Admissible under Section 65B of the Indian Evidence Act.
    """
    dossier = generate_session_dossier(
        session_id=req.session_id,
        caller_number=req.caller_number,
        callee_number=req.callee_number,
        frames=req.frames,
        operator_notes=req.operator_notes,
    )
    _DOSSIER_STORE[req.session_id] = dossier
    return {
        "status": "SEALED",
        "dossier_id": dossier["dossier_id"],
        "case_reference": dossier["case_reference"],
        "sha256_seal": dossier["cryptographic_seal"]["evidence_hash"],
        "overall_threat_level": dossier["forensic_summary"]["overall_threat_level"],
        "dossier": dossier,
    }


@router.get("/dossier/{session_id}", summary="Retrieve Sealed Forensic Dossier")
async def get_dossier_endpoint(session_id: str):
    """
    Retrieves the sealed dossier for the given session ID.
    If not previously generated, auto-generates a baseline dossier.
    """
    dossier = _DOSSIER_STORE.get(session_id)
    if not dossier:
        # Generate on-demand default
        dossier = generate_session_dossier(session_id=session_id)
        _DOSSIER_STORE[session_id] = dossier
    return dossier


@router.get("/dossier/{session_id}/download", summary="Download Dossier as Markdown or JSON")
async def download_dossier_endpoint(
    session_id: str,
    format: str = Query("markdown", pattern="^(markdown|json)$"),
):
    """
    Streams a downloadable forensic report formatted for CyberCrime (1930) or law enforcement.
    """
    dossier = _DOSSIER_STORE.get(session_id)
    if not dossier:
        dossier = generate_session_dossier(session_id=session_id)
        _DOSSIER_STORE[session_id] = dossier

    if format == "json":
        json_content = json.dumps(dossier, indent=2)
        return Response(
            content=json_content,
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="vaani-dossier-{session_id}.json"'},
        )
    else:
        md_content = ForensicDossierGenerator.to_markdown(dossier)
        return Response(
            content=md_content,
            media_type="text/markdown; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="vaani-dossier-{session_id}.md"'},
        )


@router.post("/dossier/verify", summary="Verify SHA-256 Tamper-Evidence of Dossier")
async def verify_dossier_endpoint(dossier: Dict[str, Any]):
    """
    Validates whether the dossier's evidence chain has been modified after sealing.
    """
    is_valid = verify_dossier_integrity(dossier)
    return {
        "is_valid": is_valid,
        "status": "UNALTERED_EVIDENCE" if is_valid else "TAMPERING_OR_CORRUPTION_DETECTED",
        "registered_hash": dossier.get("cryptographic_seal", {}).get("evidence_hash"),
    }


@router.get("/certificate/{session_id}", summary="Generate Section 65B Evidence Certificate (JSON)")
async def get_section_65b_certificate(session_id: str):
    """
    Returns a structured Section 65B (Indian Evidence Act) evidence certificate
    for the specified session. Includes SHA-256 chain, risk frame timeline,
    and CERT-In forensic provenance markers. Suitable for court submission.
    """
    dossier = _DOSSIER_STORE.get(session_id)
    if not dossier:
        dossier = generate_session_dossier(session_id=session_id)
        _DOSSIER_STORE[session_id] = dossier

    seal = dossier.get("cryptographic_seal", {})
    summary = dossier.get("forensic_summary", {})
    frames = dossier.get("call_frames", [])

    certificate = {
        "document_type": "SECTION_65B_EVIDENCE_CERTIFICATE",
        "statutory_authority": "Section 65B, Indian Evidence Act, 1872 (Amendment 2023)",
        "issuing_system": "VAANIRAKSHAK AI Threat Engine v1.0.0-SIH2026",
        "cert_in_framework": "CERT-In Guidelines for Electronic Evidence Preservation",
        "case_reference": dossier.get("case_reference", f"CASE-VR-{session_id[:8].upper()}"),
        "dossier_id": dossier.get("dossier_id"),
        "session_id": session_id,
        "evidence_metadata": {
            "caller_number": dossier.get("caller_number", "+91-UNKNOWN"),
            "callee_number": dossier.get("callee_number", "+91-PROTECTED"),
            "call_start_time": dossier.get("call_start_time"),
            "total_frames_analyzed": len(frames),
            "peak_risk_score": summary.get("peak_risk_score", 0),
            "overall_threat_level": summary.get("overall_threat_level", "UNKNOWN"),
            "fraud_frames_detected": summary.get("fraud_frames_detected", 0),
        },
        "cryptographic_integrity": {
            "sha256_evidence_seal": seal.get("evidence_hash"),
            "merkle_root": seal.get("merkle_root"),
            "seal_timestamp": seal.get("seal_timestamp"),
            "algorithm": "SHA-256 (FIPS 180-4)",
            "tamper_evident": True,
        },
        "risk_frame_timeline": [
            {
                "frame_index": f.get("frame_index"),
                "timestamp": f.get("timestamp"),
                "risk_score": f.get("risk_score"),
                "risk_level": f.get("risk_level"),
                "action_taken": f.get("action_taken"),
                "transcript_excerpt": f.get("transcript_excerpt", ""),
            }
            for f in frames[:20]  # First 20 frames for concise certificate
        ],
        "legal_declaration": (
            "I hereby certify under Section 65B of the Indian Evidence Act, 1872 that the "
            "electronic records contained herein were produced by VAANIRAKSHAK AI System, "
            "a computer-based tool operating in ordinary use, and that the outputs represent "
            "an accurate analysis of the voice call session identified above. The SHA-256 "
            "cryptographic seal guarantees evidence integrity from the moment of capture."
        ),
    }
    return certificate


@router.get("/certificate/{session_id}/preview", summary="Section 65B Certificate Plain-Text Preview")
async def get_certificate_preview(session_id: str):
    """
    Returns a human-readable plain-text preview of the Section 65B certificate,
    suitable for display in the dashboard modal.
    """
    cert = await get_section_65b_certificate(session_id)
    meta = cert["evidence_metadata"]
    crypto = cert["cryptographic_integrity"]

    lines = [
        "=" * 62,
        "  VAANIRAKSHAK — SECTION 65B EVIDENCE CERTIFICATE",
        "  Indian Evidence Act, 1872 | CERT-In Framework",
        "=" * 62,
        f"  Case Reference   : {cert['case_reference']}",
        f"  Dossier ID       : {cert['dossier_id']}",
        f"  Session ID       : {cert['session_id']}",
        "-" * 62,
        "  EVIDENCE METADATA",
        "-" * 62,
        f"  Caller           : {meta['caller_number']}",
        f"  Callee           : {meta['callee_number']}",
        f"  Call Start       : {meta['call_start_time']}",
        f"  Frames Analyzed  : {meta['total_frames_analyzed']}",
        f"  Peak Risk Score  : {meta['peak_risk_score']} / 100",
        f"  Threat Level     : {meta['overall_threat_level']}",
        f"  Fraud Frames     : {meta['fraud_frames_detected']}",
        "-" * 62,
        "  CRYPTOGRAPHIC INTEGRITY CHAIN",
        "-" * 62,
        f"  Algorithm        : {crypto['algorithm']}",
        f"  SHA-256 Seal     : {(crypto['sha256_evidence_seal'] or 'N/A')[:32]}...",
        f"  Sealed At        : {crypto['seal_timestamp']}",
        f"  Tamper Evident   : {'YES' if crypto['tamper_evident'] else 'NO'}",
        "-" * 62,
        "  RISK FRAME TIMELINE (first 5 frames)",
        "-" * 62,
    ]
    for f in cert["risk_frame_timeline"][:5]:
        lines.append(
            f"  Frame {f.get('frame_index', '?'):>2} | Risk: {f.get('risk_score', '?'):>3} | "
            f"{f.get('risk_level', '?'):<10} | {f.get('action_taken', '?')}"
        )
    lines += [
        "-" * 62,
        "  LEGAL DECLARATION",
        "-" * 62,
    ]
    # Word-wrap the legal declaration
    words = cert["legal_declaration"].split()
    line = "  "
    for word in words:
        if len(line) + len(word) + 1 > 62:
            lines.append(line)
            line = "  " + word + " "
        else:
            line += word + " "
    if line.strip():
        lines.append(line)
    lines.append("=" * 62)
    return {"preview": "\n".join(lines), "case_reference": cert["case_reference"]}


# ============================================================
# Carrier Telemetry Webhooks
# ============================================================

@carrier_router.post("/sip_event", summary="Carrier SIP Trunk Call Registration Webhook")
async def carrier_sip_event(req: CarrierEventRequest):
    """
    Simulates telecom carrier CDR signaling webhook.
    """
    event = carrier_adapter.register_call(req.model_dump())
    return {
        "status": "CALL_CIRCUIT_ACTIVE",
        "carrier": event.carrier_name,
        "call_id": event.call_id,
        "codec": event.codec,
        "cell_tower_cgi": event.cell_tower_cgi,
    }


@carrier_router.post("/teardown", summary="Automated Carrier Call Teardown Webhook")
async def carrier_teardown(req: CarrierTeardownRequest):
    """
    Simulates automated carrier SIP BYE call teardown triggered by fraud detection.
    """
    result = carrier_adapter.trigger_carrier_teardown(req.call_id, req.reason)
    return {
        "status": result.status,
        "sip_response_code": result.sip_response_code,
        "teardown_timestamp": result.teardown_timestamp,
        "reason": result.reason,
    }


@carrier_router.get("/telemetry/{call_id}", summary="Get Carrier Circuit Telemetry")
async def carrier_telemetry(call_id: str):
    """
    Fetches network-level telecom telemetry for an active circuit.
    Falls back to Jamtara demo mock for unknown/terminated sessions.
    """
    telemetry = carrier_adapter.get_or_mock_circuit_telemetry(call_id)
    return telemetry


@carrier_router.get("/cdr/{session_id}", summary="Get Enriched Carrier CDR & Tower Telemetry")
async def get_carrier_cdr(session_id: str):
    """
    Returns carrier-level Call Detail Record (CDR) including cell tower CGI triangulation,
    codec bitrate, packet loss, jitter, and fraud hotspot proximity.
    Phase 14: Augmented with fraud_hotspot_active, sip_circuit_state, sip_teardown_dispatched.
    Falls back to Jamtara demo mock for unknown sessions (for SIH demo continuity).
    """
    telemetry = carrier_adapter.get_or_mock_circuit_telemetry(session_id)

    # Phase 14 augmentation: SIP circuit state and fraud hotspot flags
    tower = telemetry.get("tower_location", {})
    hotspot_ref = tower.get("hotspot_ref")
    if hotspot_ref:
        telemetry["fraud_hotspot_active"] = True
        telemetry["sip_circuit_state"] = "TEARDOWN_DISPATCHED"
        telemetry["sip_teardown_dispatched"] = True
    else:
        telemetry["fraud_hotspot_active"] = False
        telemetry["sip_circuit_state"] = "ESTABLISHED"
        telemetry["sip_teardown_dispatched"] = False

    return telemetry



@carrier_router.get("/fraud-hotspots", summary="List Major Indian Telecom Fraud Hotspots")
async def get_fraud_hotspots():
    """
    Returns catalogue of high-risk telecom fraud origin clusters across India.
    """
    return carrier_adapter.get_fraud_hotspots()

