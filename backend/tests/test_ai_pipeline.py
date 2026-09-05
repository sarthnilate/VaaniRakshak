import pytest
from backend.services.ai.pipeline_aggregator import ai_pipeline


def test_multi_evidence_pipeline_processing():
    simulated_evidence = {
        "synthetic_prob": 0.96,
        "speaker_sim": 0.92,
        "transcript": "Send ₹20,000 to this UPI ID urgently.",
        "intent": "MONEY_TRANSFER",
        "tactics": ["URGENCY"],
        "risk_score": 94
    }

    res = ai_pipeline.process_chunk(
        pcm_b64="c2FtcGxl",
        preferred_language="en",
        simulated_evidence=simulated_evidence
    )

    assert res["synthetic_prob"] == 0.96
    assert res["human_prob"] == 0.04
    assert res["speaker_sim"] == 0.92
    assert res["intent"] == "MONEY_TRANSFER"
    assert "URGENCY" in res["tactics"]
    assert res["risk_score"] == 94
    assert "evidence_details" in res
    assert "authenticity" in res["evidence_details"]
    assert "biometrics" in res["evidence_details"]
    assert "stt" in res["evidence_details"]
    assert "nlp" in res["evidence_details"]
