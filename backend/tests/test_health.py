"""
Phase 0 acceptance test: the gateway boots and exposes health checks.

Dependency reachability (Redis/Postgres) is intentionally not asserted here
since this suite runs without Docker Compose in CI; /v1/health/ready is
exercised for shape only, not for a specific dependency status.
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_ok():
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"


def test_liveness_ok():
    response = client.get("/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "vaanirakshak-gateway"}


def test_readiness_has_expected_shape():
    response = client.get("/v1/health/ready")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] in {"ok", "degraded"}
    assert set(body["dependencies"].keys()) == {"redis", "database"}
