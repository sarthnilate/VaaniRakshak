import pytest
from backend.services.ai.voice_authenticity import authenticity_engine


def test_voice_authenticity_silent_chunk():
    res = authenticity_engine.analyze_audio_chunk(pcm_b64="")
    assert "synthetic_probability" in res
    assert "human_probability" in res
    assert res["synthetic_probability"] < 0.10
    assert res["engine"] == "WavLM-AASIST-v1"


def test_voice_authenticity_override():
    simulated = {"synthetic_prob": 0.96}
    res = authenticity_engine.analyze_audio_chunk(pcm_b64="dummy", simulated_override=simulated)
    assert res["synthetic_probability"] == 0.96
    assert res["human_probability"] == 0.04
