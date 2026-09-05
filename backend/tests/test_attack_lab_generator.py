import pytest
from backend.attack_lab.adapters.mock_adapter import MockResearchAdapter
from backend.attack_lab.adapters.bark_coqui_adapter import BarkCoquiAdapter
from backend.attack_lab.adapters.openvoice_adapter import OpenVoiceAdapter


@pytest.mark.asyncio
async def test_mock_generator_adapter():
    adapter = MockResearchAdapter()
    meta = adapter.metadata()
    assert meta.family == "MockResearch"

    res = await adapter.generate(
        prompt="I need your help urgently. Send ₹20,000 to this UPI ID.",
        reference_speaker_id="spk_trusted_01"
    )

    assert res.sample_id.startswith("synth_")
    assert len(res.pcm_b64) > 0
    assert res.provenance_metadata["is_synthetic"] is True
    assert res.provenance_metadata["watermark_tag"] == "VAANIRAKSHAK_ATTACK_LAB_RESEARCH_SYNTHETIC"


@pytest.mark.asyncio
async def test_bark_coqui_adapter():
    adapter = BarkCoquiAdapter()
    res = await adapter.generate(
        prompt="अपने बैंक अकाउंट का ओटीपी तुरंत बताइए",
        reference_speaker_id="spk_hindi_01",
        language="hi"
    )
    assert res.generator_family == "CoquiBark"
    assert res.language == "hi"


@pytest.mark.asyncio
async def test_openvoice_adapter():
    adapter = OpenVoiceAdapter()
    res = await adapter.generate(
        prompt="Calling from SBI security team.",
        reference_speaker_id="spk_bank_01"
    )
    assert res.generator_family == "OpenVoice"
