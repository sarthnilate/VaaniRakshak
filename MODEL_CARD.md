# Model Specification Card: VAANIRAKSHAK AI Subsystems

**Document Purpose:** Detailed technical specifications, input/output schemas, architectural parameters, and latency profiles for all AI models operating in VaaniRakshak.

---

## 1. Summary of Model Subsystems

```
                       AUDIO CHUNK (PCM 16kHz)
                                  |
         +------------------------+------------------------+
         |                        |                        |
         v                        v                        v
[1. Voice Authenticity]  [2. Speaker Biometrics]   [3. Streaming STT]
  WavLM / AASIST           ECAPA-TDNN               faster-whisper
  Output: synth_prob       Output: sim_score        Output: transcript
         |                        |                        |
         |                        |                        v
         |                        |               [4. Intent & Tactics]
         |                        |                 XLM-RoBERTa NLP
         |                        |                 Output: intent, tactics
         |                        |                        |
         +------------------------+------------------------+
                                  |
                                  v
                      [5. Temporal Risk State]
                        Rolling GRU Aggregator
                        Output: Risk Score (0-100)
```

---

## 2. Detailed Model Profiles

### Model 1: Voice Authenticity (Anti-Spoofing Engine)
- **Architecture**: Self-Supervised WavLM Large / AASIST Spectro-Temporal Model.
- **Input**: 16kHz mono 16-bit PCM audio chunk ($1.0\text{ sec} - 3.0\text{ sec}$).
- **Output**: `synthetic_probability` ($\in [0.0, 1.0]$), `artifact_score`.
- **Target Latency**: $\le 120\text{ ms}$ on GPU / $\le 220\text{ ms}$ on CPU.

### Model 2: Speaker Verification (Biometrics Engine)
- **Architecture**: ECAPA-TDNN (192-dimensional embedding space).
- **Input**: Current frame PCM + Enrolled trusted speaker 192-d embedding.
- **Output**: Cosine Similarity $S \in [-1.0, 1.0]$.
- **Target Latency**: $\le 45\text{ ms}$.

### Model 3: Multilingual STT (Speech-to-Text Engine)
- **Architecture**: `faster-whisper-small` / `medium` CTranslate2 model.
- **Input**: Rolling 1.5-second audio buffer.
- **Output**: UTF-8 text transcript, detected language code, confidence score.
- **Target Latency**: $\le 150\text{ ms}$.

### Model 4: Conversation Intelligence & Social Engineering NLP
- **Architecture**: `xlm-roberta-base` multilingual text classifier + Regex rule engine.
- **Input**: Text transcript chunk.
- **Output**: Intent tag (`MONEY_TRANSFER`, `OTP_REQUEST`, `PIN_REQUEST`), Social engineering tags (`URGENCY`, `FEAR`, `AUTHORITY`).
- **Target Latency**: $\le 35\text{ ms}$.

### Model 5: Temporal Risk Trajectory Aggregator
- **Architecture**: Gated Recurrent Unit (GRU) state network + Multi-evidence weighted fusion logic.
- **Input**: State history $S_{t-1}$ + Evidence vector $E_t = [P_{\text{synth}}, S_{\text{speaker}}, I_{\text{intent}}, T_{\text{tactic}}]$.
- **Output**: Dynamic Risk Score $R_t \in [0, 100]$ and Risk Band (`SAFE`, `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
- **Target Latency**: $\le 5\text{ ms}$.
