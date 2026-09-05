# ============================================================
# VAANIRAKSHAK — Telemetry & Deep Health Diagnostic Unit Tests
# Phase 16: Automated Verification for Metrics & Diagnostic Pings
# ============================================================
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_metrics_endpoint():
    """Verify GET /api/v1/metrics returns SLA and latency breakdowns."""
    response = client.get("/api/v1/metrics")
    assert response.status_code == 200
    data = response.json()

    assert data["sla_status"] == "COMPLIANT (<300ms SLA target)"
    assert data["target_max_latency_ms"] == 300
    assert data["total_pipeline_latency_ms"] < 300

    breakdown = data["latency_breakdown_ms"]
    assert "rawnet3_anti_spoofing" in breakdown
    assert "whisper_stt_transcription" in breakdown
    assert "ecapa_speaker_verification" in breakdown

    resources = data["system_resources"]
    assert "ram_usage_mb" in resources
    assert "cpu_utilization_pct" in resources


def test_deep_health_scan_endpoint():
    """Verify GET /api/v1/health/deep performs full component scan."""
    response = client.get("/api/v1/health/deep")
    assert response.status_code == 200
    data = response.json()

    assert data["overall_status"] == "ALL_SYSTEMS_OPERATIONAL"
    assert data["components_scanned"] >= 5

    components = [d["component"] for d in data["diagnostics"]]
    assert any("RawNet3" in c for c in components)
    assert any("Whisper" in c for c in components)
    assert any("SIP 603" in c for c in components)
