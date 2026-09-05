# ============================================================
# VAANIRAKSHAK — Spectrogram Feature Streamer Unit Tests
# Phase 20: Automated Verification for 128-Bin Mel Features
# ============================================================
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_get_spectrogram_features():
    """Verify GET /api/v1/spectrogram/features returns 128-bin Mel matrix."""
    response = client.get("/api/v1/spectrogram/features")
    assert response.status_code == 200
    data = response.json()

    assert data["sample_rate_hz"] == 16000
    assert data["mel_bins"] == 128
    assert len(data["spectrogram_matrix"]) == 30
    assert len(data["spectrogram_matrix"][0]) == 128

    metrics = data["spectral_metrics"]
    assert "spectral_centroid_hz" in metrics
    assert "zero_crossing_rate" in metrics
    assert "spectral_flux" in metrics
