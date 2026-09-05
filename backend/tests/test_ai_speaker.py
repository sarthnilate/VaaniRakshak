import pytest
from backend.services.ai.speaker_verification import speaker_engine
from backend.services.ai.audio_processor import compute_cosine_similarity


def test_cosine_similarity():
    vec1 = [1.0, 0.0, 0.0]
    vec2 = [1.0, 0.0, 0.0]
    assert pytest.approx(compute_cosine_similarity(vec1, vec2), 0.001) == 1.0

    vec3 = [-1.0, 0.0, 0.0]
    assert pytest.approx(compute_cosine_similarity(vec1, vec3), 0.001) == -1.0


def test_speaker_verification_no_enrolled():
    res = speaker_engine.verify_speaker(pcm_b64="dummy", enrolled_embeddings=[])
    assert res["speaker_similarity"] == 0.0
    assert res["is_enrolled_match"] is False


def test_speaker_verification_override():
    simulated = {"speaker_sim": 0.92}
    res = speaker_engine.verify_speaker(pcm_b64="dummy", enrolled_embeddings=[], simulated_override=simulated)
    assert res["speaker_similarity"] == 0.92
    assert res["is_enrolled_match"] is True
