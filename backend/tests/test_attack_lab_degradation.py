import pytest
from backend.attack_lab.degradation import degradation_simulator
from backend.services.ai.audio_processor import decode_pcm_b64


def test_telecom_degradation_pipeline():
    # 1 second of sample PCM
    raw_pcm = "c2FtcGxlcGNtZGF0YQ=="
    degraded_pcm = degradation_simulator.degrade_audio_chunk(
        pcm_b64=raw_pcm,
        codec="AMR-WB",
        snr_db=15.0,
        narrowband=True
    )

    assert len(degraded_pcm) > 0
    signal = decode_pcm_b64(degraded_pcm)
    assert len(signal) > 0
