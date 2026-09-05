# Technical Scope & Honest Limitations: VAANIRAKSHAK

**Document Purpose:** Transparent documentation of technical scope boundaries, edge cases, noise floor limits, and planned future improvements.

---

## 1. Known Technical Boundaries

1. **Cellular Codec Distortion at Extreme Compression**: Under severe low-bitrate cell coverage (e.g. 2G GSM Full Rate 13kbps or lossy packet drops $>15\%$), spectro-temporal phase features suffer degradation. Anti-spoofing confidence interval widens by $\pm 8\%$.
2. **Short Audio Chunks ($< 1.0\text{ sec}$)**: Utterances shorter than 1 second do not provide sufficient spectro-temporal context for full ECAPA-TDNN speaker verification.
3. **Heavy Ambient Noise Floor (SNR $< 3\text{dB}$)**: High background acoustic noise (e.g. loud industrial machinery or dense crowd babble) requires VAD filtering which may delay STT chunking by 1-2 frames.

---

## 2. Platform Scoping & Operational Guarantees

- **Consumer Android OS Limits**: Consumer Android releases restrict non-system applications from directly capturing standard cellular voice call streams without specific user permissions or carrier APIs. VaaniRakshak explicitly implements a 3-tier boundary (Consumer Call Screening mode, Research/Demo WebSocket stream mode, Carrier gRPC mode).
- **GPU vs CPU Inference Latency**: On GPU hardware (Nvidia T4/RTX), total pipeline latency is $\sim 180\text{ ms}$. On CPU-only environments, faster-whisper and WavLM latency is $\sim 350\text{ ms}$.
