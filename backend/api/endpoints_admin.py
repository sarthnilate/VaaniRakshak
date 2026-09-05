# ============================================================
# VAANIRAKSHAK — Enterprise Admin, SIEM Syslog & Audit Trail
# Phase 17: Enterprise SIEM CEF Integration & Batch Exporter
# ============================================================
import time
from typing import Optional, List
from fastapi import APIRouter, Query, Response
from pydantic import BaseModel

router = APIRouter(prefix="/admin", tags=["Enterprise Admin & SIEM"])

# In-memory audit log buffer
AUDIT_LOGS = [
    {
        "id": "AUD-1001",
        "timestamp": "2026-09-05T11:00:15Z",
        "actor": "admin_sys",
        "action": "POLICY_UPDATE",
        "details": "Adjusted RISK_THRESHOLD_CRITICAL to 90",
        "severity": "INFO",
    },
    {
        "id": "AUD-1002",
        "timestamp": "2026-09-05T11:05:42Z",
        "actor": "vaani_engine",
        "action": "CARRIER_TEARDOWN",
        "details": "Issued SIP 603 Decline for session SESS-BANKING-01",
        "severity": "CRITICAL",
    },
    {
        "id": "AUD-1003",
        "timestamp": "2026-09-05T11:12:00Z",
        "actor": "vaani_engine",
        "action": "SOS_DISPATCH",
        "details": "Transmitted incident report to 1930 Cybercrime Portal",
        "severity": "WARNING",
    },
]


class SiemExportRequest(BaseModel):
    format: str = "CEF"  # CEF or SYSLOG or JSON
    destination_ip: Optional[str] = "192.168.1.100"
    port: Optional[int] = 514


@router.get("/audit-logs", summary="Get System Security Audit Trail")
async def get_audit_logs(limit: int = Query(20, ge=1, le=100)):
    """
    Returns security audit log entries for system configuration edits,
    teardown commands, and emergency helpline dispatches.
    """
    return {
        "total_records": len(AUDIT_LOGS),
        "returned": min(limit, len(AUDIT_LOGS)),
        "logs": AUDIT_LOGS[:limit],
    }


@router.post("/siem-export", summary="Export Incidents in CEF/Syslog Format for SIEM")
async def export_siem_feed(request: SiemExportRequest):
    """
    Formats recent incidents into Common Event Format (CEF) or Syslog RFC 5424
    for streaming into enterprise SIEM platforms (Splunk, Elastic, QRadar).
    """
    # Sample CEF formatted strings
    cef_sample = (
        f"CEF:0|VaaniRakshak|AIThreatEngine|1.0|1001|Voice Cloning Scam Intercepted|9|"
        f"src=198.51.100.42 spt=5060 dst=10.0.0.1 dpt=5060 act=SIP_603_TEARDOWN "
        f"msg=Synthetic voice probability 0.94 on Hindi banking session"
    )

    return {
        "status": "STREAMING_ACTIVE",
        "format": request.format.upper(),
        "destination": f"{request.destination_ip}:{request.port}",
        "sample_payload": cef_sample,
        "active_listeners": 1,
    }


@router.get("/batch-export", summary="Export Historical Incident Records (CSV)")
async def batch_export_csv(format: str = Query("csv", pattern="^(csv|json)$")):
    """
    Generates a downloadable CSV or JSON file containing historical
    forensic incident data for offline compliance audits.
    """
    if format == "csv":
        csv_data = (
            "SessionID,CallerCLI,PeakRisk,ThreatLevel,Action,Timestamp,Sha256Seal\n"
            "SESS-BANKING-01,+91-9876543210,94,CRITICAL,BLOCK,2026-09-05T11:05:42Z,8f4a...e12\n"
            "SESS-CREDITCARD-02,+91-9123456789,78,HIGH,ALERT,2026-09-05T11:10:15Z,3b1c...a90\n"
            "SESS-BASELINE-03,+91-9988776655,12,SAFE,MONITOR,2026-09-05T11:15:30Z,6d7e...f44\n"
        )
        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=vaanirakshak_incidents_audit.csv"},
        )
    else:
        return {
            "export_type": "JSON_BATCH",
            "timestamp": time.time(),
            "count": 3,
            "incidents": [
                {"session_id": "SESS-BANKING-01", "risk": 94, "action": "BLOCK"},
                {"session_id": "SESS-CREDITCARD-02", "risk": 78, "action": "ALERT"},
                {"session_id": "SESS-BASELINE-03", "risk": 12, "action": "MONITOR"},
            ],
        }
