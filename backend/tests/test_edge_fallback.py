# ============================================================
# VAANIRAKSHAK — Air-Gapped Edge Engine Unit Tests
# Phase 19: Automated Verification for Local ONNX Fallback
# ============================================================
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.ai.edge_fallback import edge_engine

client = TestClient(app)


def test_edge_status_endpoint():
    """Verify GET /api/v1/edge/status returns NPU and RAM metrics."""
    response = client.get("/api/v1/edge/status")
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "OPERATIONAL"
    assert "ram_footprint_mb" in data
    assert data["ram_footprint_mb"] < 150.0  # Mobile RAM bound SLA


def test_edge_toggle_endpoint():
    """Verify POST /api/v1/edge/toggle toggles air-gapped mode."""
    response = client.post("/api/v1/edge/toggle", json={"air_gapped_offline": True})
    assert response.status_code == 200
    assert response.json()["air_gapped_offline"] is True
    assert edge_engine.is_offline_mode is True

    # Revert to Hybrid Cloud mode
    client.post("/api/v1/edge/toggle", json={"air_gapped_offline": False})
    assert edge_engine.is_offline_mode is False


def test_process_local_chunk():
    """Verify POST /api/v1/edge/process-local executes zero-cloud local inference."""
    response = client.post("/api/v1/edge/process-local")
    assert response.status_code == 200
    data = response.json()

    assert "synthetic_probability" in data
    assert data["cloud_connection"] is False
    assert data["local_inference_ms"] < 30.0
