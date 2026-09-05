# PRD: VAANIRAKSHAK — AI-Powered Real-Time Voice Cloning Impersonation Detection & Prevention Engine

**SIH Problem Statement:** SIH26104 — AI-Powered Real-Time Detection and Prevention of Voice Cloning Impersonation Attacks  
**Target Platform:** Android Security Product + Python FastAPI Real-Time AI Threat Engine + React Live Command Dashboard  
**Classification:** Modular, Privacy-First Production Defense Engine & Controlled Research Attack Lab  

---

## 1. Executive Summary & Vision
VAANIRAKSHAK ("Voice Protector") is a real-time, privacy-first phone security engine designed to protect individuals and organizations against AI voice cloning, deepfake audio impersonation, and voice-based social engineering scams.

Unlike basic binary deepfake classifiers or UI prototypes, VaaniRakshak evaluates incoming voice calls across multiple independent evidence vectors—combining physical acoustic anti-spoofing, speaker biometric verification, multilingual speech-to-text (STT), intent classification, social engineering detection, and temporal risk trajectory modeling.

The project is structured into two completely isolated systems:
1. **System A: Attack Lab** — A consent-governed research and demonstration environment for generating synthetic voice samples using modular voice-cloning adapters with provenance tracking.
2. **System B: VaaniRakshak Defense Engine** — The core defensive platform comprising an Android call protection application, a multi-evidence backend risk engine, and a live security command dashboard.

---

## 2. Core System Architecture Overview

```
                      +---------------------------------------+
                      |         SYSTEM A: ATTACK LAB          |
                      | (Controlled Synthetic Audio Lab)      |
                      +---------------------------------------+
                                          |
                                          | (Synthetic Attack Audio Stream)
                                          v
+-----------------------------------------------------------------------------------+
|                       SYSTEM B: VAANIRAKSHAK DEFENSE ENGINE                        |
|                                                                                   |
|  +------------------------+      +-------------------------------+                |
|  |     ANDROID CLIENT     |      |      REAL-TIME AI ENGINE      |                |
|  | CallScreeningService   |=====>| Voice Authenticity (WavLM)    |                |
|  | Dynamic Security HUD   | WS   | Speaker Verification (ECAPA)  |                |
|  | User Policies          |      | Multilingual STT (Whisper)    |                |
|  +------------------------+      | Intent & Social Eng (XLM-R)   |                |
|                                  | Temporal Risk GRU Engine      |                |
|  +------------------------+      +-------------------------------+                |
|  |    REACT DASHBOARD     |                      |                                |
|  | Live Command Center    |<=====================+ (Metrics, State, Incidents)     |
|  +------------------------+          Redis / Supabase (PostgreSQL)                |
+-----------------------------------------------------------------------------------+
```

---

## 3. Detailed Specifications: System A — Attack Lab

### 3.1 Purpose & Ethics Boundaries
- **Strict Consent Enforcement**: Attack Lab operates exclusively on explicitly consented reference voices, benchmark open datasets, or synthetic baseline samples.
- **Non-Covert Guarantee**: Generated audio MUST embed cryptographic/watermark provenance metadata identifying the sample as synthetic (`is_synthetic: true`, `generator_id`, `timestamp`, `consent_hash`).
- **Research Utility**: Used solely to demonstrate defense capabilities during SIH evaluation and generate attack vectors for defensive training.

### 3.2 Modular Generator Adapter Interface
The Attack Lab MUST NOT be tightly coupled to any single voice cloning model. It uses a decoupled adapter contract:

```python
class VoiceGenerator(ABC):
    @abstractmethod
    async def generate(self, prompt: str, reference_speaker_id: str, language: str) -> SyntheticAudioResult:
        """Generates synthetic audio given text prompt and reference speaker profile."""
        pass

    @abstractmethod
    def validate_reference(self, reference_audio_path: str) -> ValidationResult:
        """Validates sample length, noise floor, and speaker consent metadata."""
        pass

    @abstractmethod
    def supported_languages(self) -> List[str]:
        """Returns ISO language codes supported by this engine adapter."""
        pass

    @abstractmethod
    def metadata(self) -> GeneratorMetadata:
        """Returns generator family, model version, and capability profile."""
        pass
```

### 3.3 Supported Adapter Engines
1. **Local Bark / Coqui XTTS Adapter** — Zero-shot multilingual voice cloning.
2. **OpenVoice / StyleTTS2 Adapter** — High-speed spectro-temporal cloning.
3. **ElevenLabs / Third-Party Cloud Adapter** — High-fidelity cloud baseline (optional API key driven).
4. **Mock Research Generator** — Fast offline generator for automated pipeline unit tests.

---

## 4. Detailed Specifications: System B — VaaniRakshak Defense Engine

### 4.1 Android Client Architecture & User Journeys
- **Onboarding Flow**:
  1. **Permission Explanation**: Transparent rationale for `CallScreeningService`, `READ_CONTACTS`, `POST_NOTIFICATIONS`, and `RECORD_AUDIO` (Research/Demo mode).
  2. **Role Manager Integration**: Requests default `ROLE_CALL_SCREENING` to intercept incoming calls automatically.
  3. **Protection Policy Setup**:
     - *Unknown Numbers*: Automatically protected by default.
     - *Known Contacts*: Protected or exempted based on user preference.
     - *Intervention Policy*: Configurable emergency action threshold (default: 10-second confirmation window before auto-termination/alert).
  4. **Consented Speaker Enrollment**: Allows users to enroll voice embeddings of family members/trusted contacts with explicit consent.

- **Live Call Experience**:
  - **Non-Intrusive Security Indicator HUD**: Small floating badge (`🛡 Protected | Risk 37/100`) with a smooth dynamic color bar.
  - **Dynamic Progression**: Updates in near-real-time as audio chunks are processed (`32 -> 58 -> 78 -> 94`).
  - **Critical Intervention Window**: When risk score reaches $\ge 90$, displays prominent alert UI with countdown timer (10s configurable), threat breakdown, and one-tap emergency termination or verification challenge.

### 4.2 Multi-Evidence AI Risk Engine Architecture

```
                       AUDIO CHUNK (PCM 16kHz)
                                  |
            +---------------------+---------------------+
            |                     |                     |
            v                     v                     v
   VOICE AUTHENTICITY    SPEAKER VERIFICATION          STT
   (WavLM / AASIST)       (ECAPA-TDNN)          (faster-whisper)
   - Synthetic Prob       - Speaker Similarity          |
   - Human Prob           - Anomaly Score        Transcribed Text
   - Artifact Score               |                     |
            |                     |                     v
            |                     |           INTENT & SOCIAL ENG
            |                     |           (XLM-RoBERTa / Rules)
            |                     |           - Intent: MONEY, OTP, PIN
            |                     |           - Tactics: URGENCY, FEAR
            |                     |                     |
            +---------------------+---------------------+
                                  |
                                  v
                        TEMPORAL STATE ENGINE
                        (GRU State Tracker)
                                  |
                                  v
                             RISK ENGINE
                  Risk = f(Evidence_1...N, History)
                                  |
                                  v
                           DECISION ENGINE
                  (SAFE / LOW / MED / HIGH / CRITICAL)
```

#### Evidence Breakdown & Outputs:
1. **Voice Authenticity**: Anti-spoofing model detecting spectro-temporal artifacts, phase irregularities, and codec degradation. Output: `synthetic_probability` ($0.0 - 1.0$), `confidence`.
2. **Speaker Verification**: Computes cosine similarity between incoming speaker embedding and enrolled trusted profile.
   - *Crucial Rule*: High similarity + High synthetic score = **Voice Impersonation Attack** (e.g. `speaker_similarity: 0.92`, `synthetic_prob: 0.96`).
3. **Speech-to-Text (STT)**: Multilingual streaming STT chunking audio into rolling text frames.
4. **Conversation Intelligence & Intent**: Classifies text frames for high-risk intents (`MONEY_TRANSFER`, `OTP_REQUEST`, `PIN_REQUEST`, `REMOTE_ACCESS`, `APK_INSTALLATION`, etc.).
5. **Social Engineering Detection**: Identifies psychological manipulation tactics (`URGENCY`, `FEAR`, `AUTHORITY`, `SECRECY`, `PRESSURE`).
6. **Temporal State Modeling**: Rolling GRU network tracking risk trajectory across time steps to prevent single-word false positives while ensuring swift reaction ($\le 3$ seconds).
7. **Risk Score & Bands**:
   - `0 - 29`: **SAFE** (Green badge)
   - `30 - 59`: **LOW** (Blue badge)
   - `60 - 79`: **MEDIUM** (Yellow badge)
   - `80 - 89`: **HIGH** (Orange badge)
   - `90 - 100`: **CRITICAL** (Red badge + Intervention trigger)

---

## 5. Required SIH Demonstration Scenarios

### Scenario 1: Real Voice Call (Legitimate Contact)
- **Flow**: Enrolled trusted contact or normal user calls the protected phone.
- **Evidence**: `synthetic_probability: 0.04`, `speaker_similarity: 0.94`, `threat_intent: NONE`.
- **Result**: Risk score remains low ($\sim 12/100$). Call proceeds normally without disturbance.

### Scenario 2: AI Cloned Voice Attack (Impersonation Fraud)
- **Flow**: Attack Lab generates a synthetic clone of an enrolled trusted speaker saying: *"I need your help urgently. Please send ₹20,000 to this UPI ID right now."*
- **Evidence**:
  - `synthetic_probability: 0.96`
  - `speaker_similarity: 0.92` (Resembles trusted speaker)
  - `intent: MONEY_TRANSFER`
  - `tactic: URGENCY`
- **Trajectory**: $32 \rightarrow 58 \rightarrow 78 \rightarrow 94$.
- **Result**: Reaches **CRITICAL** ($94/100$). Dynamic HUD turns red $\rightarrow$ 10-second countdown activates $\rightarrow$ **🚨 VOICE IMPERSONATION DETECTED** banner $\rightarrow$ Call Terminated / Protected $\rightarrow$ Polished animated explanation view opens.

### Scenario 3: Real Human Scammer (Social Engineering Fraud)
- **Flow**: Genuine human scammer calls pretending to be a bank official: *"I am calling from SBI security department. Provide your OTP immediately or your account will be blocked."*
- **Evidence**:
  - `synthetic_probability: 0.06` (Genuine human voice)
  - `speaker_similarity: 0.15` (Unknown speaker)
  - `intent: OTP_REQUEST / BANK_VERIFICATION`
  - `tactic: AUTHORITY / FEAR / URGENCY`
- **Result**: Overall risk escalates to **CRITICAL** ($91/100$). Proves **VaaniRakshak is an all-around voice threat engine**, not just a deepfake audio classifier!

---

## 6. Multilingual Requirements
- Supported Priority Indian Languages: English, Hindi, Hinglish, Marathi, Bengali, Tamil, Telugu, Kannada, Malayalam, Gujarati, Punjabi, Urdu, Odia, Assamese, Nepali, Sanskrit.
- Multilingual STT engine with automatic language identification.
- Intent & Social Engineering classifier built on multilingual transformer encoders (XLM-RoBERTa).

---

## 7. Privacy & Security Directives
- **Zero Raw Audio Persistence**: Raw audio PCM frames exist ONLY in volatile RAM during inference window and are instantly discarded.
- **On-Device Profile Embeddings**: Enrolled speaker profiles store feature vectors (embeddings), NEVER raw audio recordings.
- **Deterministic Action Layer**: Call termination and alerting policies are driven by deterministic threshold rules and temporal GRU state—**NEVER directly by generative LLMs**.
