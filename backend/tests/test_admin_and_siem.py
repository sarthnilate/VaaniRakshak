# ============================================================
# VAANIRAKSHAK — Enterprise Admin & SIEM Unit Tests
# Phase 17: Automated Verification for CEF Export & Audit Logs
# ============================================================
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_get_audit_logs():
    """Verify GET /api/v1/admin/audit-logs returns security audit log buffer."""
    response = client.get("/api/v1/admin/audit-logs")
    assert response.status_code == 200
    data = response.json()

    assert data["total_records"] >= 3
    logs = data["logs"]
    assert any(l["action"] == "POLICY_UPDATE" for l in logs)
    assert any(l["action"] == "CARRIER_TEARDOWN" for l in logs)


def test_post_siem_export_cef():
    """Verify POST /api/v1/admin/siem-export formats CEF payload correctly."""
    response = client.post(
        "/api/v1/admin/siem-export",
        json={"format": "CEF", "destination_ip": "10.0.0.5", "port": 514},
    )
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "STREAMING_ACTIVE"
    assert data["destination"] == "10.0.0.5:514"
    assert "CEF:0|VaaniRakshak|" in data["sample_payload"]
    assert "act=SIP_603_TEARDOWN" in data["sample_payload"]


def test_batch_export_csv():
    """Verify GET /api/v1/admin/batch-export returns CSV formatted response."""
    response = client.get("/api/v1/admin/batch-export?format=csv")
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "SessionID,CallerCLI,PeakRisk" in response.text
    assert "SESS-BANKING-01" in response.text
