"""
============================================================
VAANIRAKSHAK — Phase 14 Test Suite
Carrier CDR Geolocation, Fraud Hotspot Catalog & SIP 603 Teardown
============================================================
"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.carrier.sip_trunk_adapter import (
    CarrierSipTrunkAdapter,
    CellTowerLocation,
    INDIAN_FRAUD_HOTSPOTS,
)

client = TestClient(app)

# ─── Adapter Unit Tests ──────────────────────────────────────────────────────

def test_fraud_hotspot_catalog_not_empty():
    """Fraud hotspot catalog must contain at least 4 clusters."""
    assert len(INDIAN_FRAUD_HOTSPOTS) >= 4


def test_fraud_hotspot_fields_present():
    """Every hotspot entry must contain required fields."""
    required = {"hotspot_id", "region_name", "latitude", "longitude", "risk_index", "primary_modus_operandi", "active_sim_farms", "status"}
    for hs in INDIAN_FRAUD_HOTSPOTS:
        assert required.issubset(hs.keys()), f"Missing fields in {hs.get('hotspot_id')}"


def test_fraud_hotspot_risk_index_bounds():
    """All risk indices must be in range [0, 100]."""
    for hs in INDIAN_FRAUD_HOTSPOTS:
        assert 0 <= hs["risk_index"] <= 100, f"Out-of-range risk_index: {hs}"


def test_jamtara_hotspot_highest_risk():
    """Jamtara cluster should have the highest risk index."""
    jamtara = next((h for h in INDIAN_FRAUD_HOTSPOTS if "Jamtara" in h["region_name"]), None)
    assert jamtara is not None, "Jamtara hotspot missing"
    max_risk = max(h["risk_index"] for h in INDIAN_FRAUD_HOTSPOTS)
    assert jamtara["risk_index"] == max_risk


def test_tower_resolution_jamtara_cgi():
    """CGI containing '8192' should resolve to Jamtara tower."""
    adapter = CarrierSipTrunkAdapter()
    tower: CellTowerLocation = adapter._resolve_tower_location("404-45-8192-3021")
    assert "Jamtara" in tower.region_name
    assert tower.is_known_fraud_corridor is True
    assert tower.hotspot_ref == "HOTSPOT-JAMTARA-01"
    assert abs(tower.latitude - 23.9629) < 0.001


def test_tower_resolution_mewat_cgi():
    """CGI containing '7701' should resolve to Mewat/Nuh tower."""
    adapter = CarrierSipTrunkAdapter()
    tower: CellTowerLocation = adapter._resolve_tower_location("404-20-7701-0109")
    assert "Mewat" in tower.region_name
    assert tower.is_known_fraud_corridor is True
    assert tower.hotspot_ref == "HOTSPOT-MEWAT-02"


def test_tower_resolution_unknown_cgi_default():
    """Unknown CGI should fall back to NCR default without fraud flag."""
    adapter = CarrierSipTrunkAdapter()
    tower: CellTowerLocation = adapter._resolve_tower_location("404-10-9999-0001")
    assert tower.is_known_fraud_corridor is False
    assert tower.hotspot_ref is None


def test_register_call_and_telemetry():
    """Registered call should return full CDR telemetry with tower info."""
    adapter = CarrierSipTrunkAdapter()
    call = adapter.register_call({
        "call_id": "test-cdr-phase14",
        "calling_party": "+91-9876543210",
        "called_party": "+91-1234567890",
        "cell_tower_cgi": "404-45-8192-3021",
        "codec": "AMR-WB/23850",
        "packet_loss_pct": 1.5,
        "jitter_ms": 4.8,
    })
    assert call.call_id == "test-cdr-phase14"
    assert call.tower_location is not None
    assert "Jamtara" in call.tower_location.region_name

    telemetry = adapter.get_circuit_telemetry("test-cdr-phase14")
    assert telemetry is not None
    assert telemetry["tower_location"]["is_known_fraud_corridor"] is True
    assert telemetry["network_telemetry"]["packet_loss_pct"] == 1.5


def test_sip_603_teardown_success():
    """SIP 603 teardown on an active circuit should succeed with code 603."""
    adapter = CarrierSipTrunkAdapter()
    adapter.register_call({"call_id": "teardown-test-01", "calling_party": "+91-0000000000", "called_party": "+91-1111111111"})
    result = adapter.trigger_carrier_teardown("teardown-test-01", reason="UNIT_TEST")
    assert result.sip_response_code == 603
    assert result.status == "CIRCUIT_TERMINATED"
    assert "UNIT_TEST" in result.reason


def test_sip_481_teardown_nonexistent_circuit():
    """SIP teardown on non-existent circuit should return 481 Call Leg Unavailable."""
    adapter = CarrierSipTrunkAdapter()
    result = adapter.trigger_carrier_teardown("ghost-session-99999")
    assert result.sip_response_code == 481
    assert "NOT_FOUND" in result.status


# ─── REST API Integration Tests ──────────────────────────────────────────────

def test_api_fraud_hotspots_endpoint():
    """GET /api/v1/carrier/fraud-hotspots should return a list with 4+ entries."""
    res = client.get("/api/v1/carrier/fraud-hotspots")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 4


def test_api_cdr_with_fraud_session():
    """GET /api/v1/carrier/cdr/{session_id} for Jamtara session should flag fraud corridor."""
    res = client.get("/api/v1/carrier/cdr/sess_sih_showcase_01")
    assert res.status_code == 200
    data = res.json()
    assert data["fraud_hotspot_active"] is True
    assert data["tower_location"]["is_known_fraud_corridor"] is True
    assert "TEARDOWN" in data["sip_circuit_state"]


def test_api_cdr_fallback_for_unknown_session():
    """GET /api/v1/carrier/cdr for an unknown session should return fallback mock data (not 404)."""
    res = client.get("/api/v1/carrier/cdr/sess_unknown_xyz_phase14")
    assert res.status_code == 200
    data = res.json()
    assert "tower_location" in data
    assert "network_telemetry" in data


def test_api_teardown_endpoint():
    """POST /api/v1/carrier/teardown should return valid SIP response."""
    res = client.post("/api/v1/carrier/teardown/sess_sih_showcase_01")
    assert res.status_code == 200
    data = res.json()
    assert data["sip_response_code"] in (603, 481)
    assert "message" in data
