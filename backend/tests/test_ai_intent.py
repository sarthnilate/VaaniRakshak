import pytest
from backend.services.ai.intent_nlp import intent_engine


def test_intent_detection_money_and_urgency():
    transcript = "I need your help urgently. Send ₹20,000 to this UPI ID right now."
    res = intent_engine.analyze_transcript(transcript)
    assert res["detected_intent"] == "MONEY_TRANSFER"
    assert "URGENCY" in res["detected_tactics"]
    assert res["is_high_risk"] is True


def test_intent_detection_otp_and_authority_hindi():
    transcript = "बैंक अधिकारी बोल रहा हूँ। अपना ओटीपी तुरंत बताइए वरना अकाउंट ब्लॉक हो जाएगा।"
    res = intent_engine.analyze_transcript(transcript)
    assert res["detected_intent"] == "OTP_REQUEST" or res["detected_intent"] == "BANK_VERIFICATION"
    assert "URGENCY" in res["detected_tactics"] or "AUTHORITY" in res["detected_tactics"] or "FEAR" in res["detected_tactics"]
    assert res["is_high_risk"] is True


def test_intent_detection_normal_convo():
    transcript = "Hey brother, let's catch up for coffee tomorrow afternoon."
    res = intent_engine.analyze_transcript(transcript)
    assert res["detected_intent"] == "NORMAL_CONVERSATION"
    assert len(res["detected_tactics"]) == 0
    assert res["is_high_risk"] is False
