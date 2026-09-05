import pytest
from backend.attack_lab.provenance import provenance_tracker


def test_provenance_tracker_creation_and_verification():
    prov = provenance_tracker.create_provenance(
        sample_id="synth_test_101",
        generator_family="CoquiBark",
        prompt="Test research script",
        reference_speaker_id="spk_001"
    )

    assert prov["is_synthetic"] is True
    assert prov["generator_family"] == "CoquiBark"
    assert prov["watermark_tag"] == "VAANIRAKSHAK_ATTACK_LAB_RESEARCH_SYNTHETIC"
    assert len(prov["consent_hash"]) == 64

    assert provenance_tracker.verify_provenance(prov) is True


def test_provenance_tracker_verification_invalid():
    invalid_prov = {
        "is_synthetic": False,
        "watermark_tag": "INVALID"
    }
    assert provenance_tracker.verify_provenance(invalid_prov) is False
