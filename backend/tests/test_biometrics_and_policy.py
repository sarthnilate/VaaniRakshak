"""
============================================================
Phase 12 — Biometric Profile Vault & Policy Matrix Tests
============================================================
Verifies:
  - 192-d ECAPA-TDNN biometric profile vault and cosine matching
  - Privacy consent invariants (rejection on non-consent, deletion on revocation)
  - Dynamic policy matrix configuration endpoints (thresholds, intervention window)
  - Validation bounds (threshold order enforcement)
  - Incident history ledger API integration
"""
import pytest
import numpy as np
from fastapi.testclient import TestClient

from backend.main import app
from backend.services.biometrics.profile_vault import (
    BiometricProfileVault,
    EnrolledVoiceProfile,
)


class TestBiometricProfileVault:
    """Verifies privacy-first 192-d biometric voice profile vault."""

    def test_default_seeded_profiles(self):
        vault = BiometricProfileVault()
        profiles = vault.list_profiles()
        assert len(profiles) >= 2
        names = [p["display_name"] for p in profiles]
        assert "Rahul (Son)" in names
        assert "Priya (Daughter)" in names
        # Verify raw embeddings are not exposed in list_profiles
        assert "embedding" not in profiles[0]

    def test_enrollment_requires_explicit_consent(self):
        vault = BiometricProfileVault()
        dummy_vec = [0.1] * 192
        with pytest.raises(ValueError, match="consent is legally mandatory"):
            vault.enroll_profile(
                display_name="Test Imposter",
                phone_number="+91-1111111111",
                embedding=dummy_vec,
                consent_given=False,
            )

    def test_enrollment_requires_exact_192_dimensions(self):
        vault = BiometricProfileVault()
        with pytest.raises(ValueError, match="must be exactly 192 dimensions"):
            vault.enroll_profile(
                display_name="Bad Vec",
                phone_number="+91-1111111111",
                embedding=[0.5] * 100,  # Invalid dimension
                consent_given=True,
            )

    def test_cosine_similarity_matching_exact(self):
        vault = BiometricProfileVault()
        # Fetch Rahul's embedding
        rahul = vault.get_profile("spk_rahul_son")
        assert rahul is not None

        # Query with exact same embedding
        res = vault.match_speaker(rahul.embedding)
        assert res["is_match"] is True
        assert res["best_similarity"] > 0.95
        assert res["matched_profile"]["speaker_id"] == "spk_rahul_son"

    def test_cosine_similarity_matching_different_speaker(self):
        vault = BiometricProfileVault()
        # Query with orthogonal or inverted random vector
        rng = np.random.RandomState(999)
        unrelated = rng.randn(192).tolist()

        res = vault.match_speaker(unrelated)
        assert res["best_similarity"] < vault.MATCH_THRESHOLD
        assert res["is_match"] is False

    def test_revoke_consent_and_deletion(self):
        vault = BiometricProfileVault()
        dummy_vec = [0.05] * 192
        vault.enroll_profile(
            speaker_id="temp_speaker_01",
            display_name="Temporary User",
            phone_number="+91-0000000000",
            embedding=dummy_vec,
            consent_given=True,
        )
        assert vault.get_profile("temp_speaker_01") is not None

        # Revoke
        deleted = vault.revoke_consent("temp_speaker_01")
        assert deleted is True
        assert vault.get_profile("temp_speaker_01") is None


class TestDynamicPolicyEndpoints:
    """Verifies REST endpoints for live defense policy tuning."""

    def test_get_active_policy(self):
        with TestClient(app) as client:
            res = client.get("/api/v1/policy")
            assert res.status_code == 200
            data = res.json()
            assert data["status"] == "ACTIVE"
            assert "intervention_window_sec" in data["policy"]
            assert data["policy"]["critical_threshold"] >= 70

    def test_update_policy_valid(self):
        with TestClient(app) as client:
            update_payload = {
                "intervention_window_sec": 15,
                "critical_threshold": 90,
                "high_threshold": 70,
                "medium_threshold": 40,
                "low_threshold": 20,
                "auto_block_enabled": True,
                "operational_tier": "TIER_3_CARRIER",
                "screening_unknown_numbers_only": False,
            }
            res = client.post("/api/v1/policy/update", json=update_payload)
            assert res.status_code == 200
            data = res.json()
            assert data["status"] == "POLICY_UPDATED"
            assert data["policy"]["intervention_window_sec"] == 15
            assert data["policy"]["critical_threshold"] == 90
            assert data["policy"]["operational_tier"] == "TIER_3_CARRIER"

    def test_update_policy_invalid_threshold_order(self):
        with TestClient(app) as client:
            # Low threshold greater than high threshold
            bad_payload = {
                "intervention_window_sec": 10,
                "critical_threshold": 75,
                "high_threshold": 80,  # Invalid: high > critical
                "medium_threshold": 40,
                "low_threshold": 20,
            }
            res = client.post("/api/v1/policy/update", json=bad_payload)
            assert res.status_code == 400
            assert "ordering" in res.json()["detail"]

    def test_reset_policy_to_defaults(self):
        with TestClient(app) as client:
            res = client.post("/api/v1/policy/reset")
            assert res.status_code == 200
            data = res.json()
            assert data["status"] == "RESET_TO_DEFAULTS"
            assert data["policy"]["intervention_window_sec"] == 10


class TestIncidentAndSpeakerEndpoints:
    """Verifies incident retrieval and speaker API endpoints."""

    def test_list_incidents_endpoint(self):
        with TestClient(app) as client:
            res = client.get("/api/v1/incidents")
            assert res.status_code == 200
            assert isinstance(res.json(), list)

    def test_speaker_enrollment_rejects_without_consent(self):
        with TestClient(app) as client:
            res = client.post("/api/v1/speakers/enroll", json={
                "display_name": "Unconsented Target",
                "phone_number": "+91-9999900000",
                "embedding": [0.1] * 192,
                "consent_given": False,
            })
            assert res.status_code in [400, 422]
            assert "consent is mandatory" in str(res.json()).lower()
