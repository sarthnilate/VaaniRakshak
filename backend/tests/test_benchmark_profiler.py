# ============================================================
# VAANIRAKSHAK — AI Resiliency Benchmark Profiler Unit Tests
# Phase 18: Automated Verification for Telecom Degradation Suite
# ============================================================
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_run_resiliency_benchmark():
    """Verify GET /api/v1/benchmarks/run profiles model degradation conditions."""
    response = client.get("/api/v1/benchmarks/run")
    assert response.status_code == 200
    data = response.json()

    assert data["composite_grade"] == "A+ (Production Telecom Grade)"
    assert data["summary_metrics"]["conditions_passed"] >= 5

    profiles = data["profiles"]
    condition_ids = [p["condition_id"] for p in profiles]
    assert "PSTN_8KHZ" in condition_ids
    assert "G711_ALAW" in condition_ids
    assert "SNR_10DB_NOISE" in condition_ids

    # Verify every condition passed
    assert all(p["status"] == "PASS" for p in profiles)
