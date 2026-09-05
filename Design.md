# Visual & Interaction Design Specifications: VAANIRAKSHAK

**Design Philosophy:** Modern Cyber-Security, High-Trust Privacy Aesthetic  
**Target Interfaces:** Android Jetpack Compose Mobile UI + React 18 / Tailwind Web Command Center  

---

## 1. Core Color Palette & Design Tokens

To deliver a state-of-the-art, premium security experience, VaaniRakshak utilizes a high-contrast dark theme palette with vivid, semantic status indicators:

```gdb
/* Background & Surface Tokens */
--color-bg-primary:     #0B0F19   (Obsidian Dark Core)
--color-bg-secondary:   #111827   (Deep Slate Card Background)
--color-bg-tertiary:    #1F2937   (Interactive Component Surface)
--color-border:         #374151   (Subtle Glass Border)

/* Brand & Accent Tokens */
--color-brand-cyan:     #06B6D4   (Vibrant Cyber Blue - Primary Accent)
--color-brand-indigo:   #6366F1   (Deep Intelligence Indigo)

/* Risk Level Semantic Status Tokens */
--color-risk-safe:      #10B981   (Emerald Green - Risk 0 to 29)
--color-risk-low:       #3B82F6   (Royal Blue - Risk 30 to 59)
--color-risk-medium:    #F59E0B   (Amber Gold - Risk 60 to 79)
--color-risk-high:      #F97316   (Vivid Orange - Risk 80 to 89)
--color-risk-critical:  #EF4444   (Crimson Red - Risk 90 to 100)
```

---

## 2. Android Live Call HUD & User Experience

### 2.1 Minimal Floating Call Badge Overlay
During an active call, the phone's native call UI remains dominant. VaaniRakshak renders a minimal floating security badge at the top-right or top-center:

```
+-------------------------------------------------------------+
|                                                             |
|                    [  🛡 Protected | Risk 37/100  ]         |
|                       [====================      ]          |
|                                                             |
|                      INCOMING CELLULAR CALL                 |
|                            Unknown Caller                   |
|                            +91 98765 43210                  |
|                                                             |
|                     ( Answer )     ( Decline )              |
+-------------------------------------------------------------+
```

#### States & Micro-Animations:
- **SAFE ($0 - 29$)**: Emerald green badge icon (`🛡 Protected`). Dynamic progress bar fills to current risk percentage.
- **LOW ($30 - 59$)**: Royal blue badge icon. Smooth animated bar transition.
- **MEDIUM ($60 - 79$)**: Amber gold badge icon. Slight pulse effect on risk change.
- **HIGH ($80 - 89$)**: Orange warning badge icon. Subtle border glow animation.
- **CRITICAL ($90 - 100$)**: Crimson red alert mode. Converts into the full **Emergency Intervention View**.

---

### 2.2 Emergency Intervention Overlay UI
When risk score reaches $\ge 90$ (e.g. $94/100$), the system triggers the 10-second intervention policy window:

```
+-------------------------------------------------------------+
| 🚨 VOICE IMPERSONATION DETECTED                             |
|                                                             |
|                        94 / 100                             |
|                        CRITICAL                             |
|                                                             |
|  Auto-Terminating Call in: [ 08s ]                           |
|                                                             |
|  Threat Evidence Breakdown:                                 |
|  - Synthetic Voice Prob:  96%  [CRITICAL]                   |
|  - Speaker Similarity:    92%  [IMPERSONATION DETECTED]     |
|  - Financial Request:     DETECTED (₹20,000 UPI)            |
|  - Social Engineering:    URGENCY DETECTED                  |
|                                                             |
|  [ TERMINATE & BLOCK NOW ]     [ IGNORE / CONTINUE CALL ]   |
+-------------------------------------------------------------+
```

---

### 2.3 Post-Call Animated Explanation Screen
Following call termination or high-risk alert, the user is presented with a detailed, accessible security breakdown:

- **Header**: "Call Threat Intercepted" with an animated green/red shield graphic.
- **Evidence Cards**:
  - *Voice Authenticity Spectrogram*: Visual representation of synthetic phase artifacts.
  - *Speaker Biometrics*: Enrolled voice vs. incoming call feature comparison graph.
  - *Transcript & Risk Trigger Highlighting*: Text display highlighting detected fraud phrases (*"send ₹20,000 urgently"*).
- **Actions**: "Report to CyberCrime (1930)", "Add to Blocklist", "Export Incident Report (PDF/JSON)".

---

## 3. React Live Security Command Center Dashboard Layout

The Web Command Center is designed for security administrators, technical judges, and security analysts:

```
+-----------------------------------------------------------------------------------+
|  🛡 VAANIRAKSHAK COMMAND CENTER               [ LIVE SESSION: sess_89f2a0 ]  [● LIVE] |
+------------------------------------+----------------------------------------------+
| REAL-TIME RISK RADAR               | VOICE AUTHENTICITY SPECTRUM                 |
|                                    |                                              |
|            Critical (94)           |  Human Prob:      [====      ] 4%            |
|              /\                    |  Synthetic Prob:  [==========] 96%           |
|             /  \                   |                                              |
|            /    \                  | SPECTROGRAM WATERMARK ANALYSIS               |
|  Speaker  /      \  Intent         | [||||||||||||||||||||||||||||||||||||||||||] |
|   (92%)  /________\  (Money/Urgent)| Synthetic Artifact Pattern Detected at 2.4kHz|
+------------------------------------+----------------------------------------------+
| LIVE MULTILINGUAL TRANSCRIPT       | THREAT EVIDENCE VECTOR LIST                  |
|                                    |                                              |
| [14:02:11] "Hello brother..."      | ● SYNTHETIC_VOICE_SCORE: 0.96 (WavLM)        |
| [14:02:14] "I need your help       | ● SPEAKER_SIMILARITY:    0.92 (ECAPA-TDNN)   |
|  urgently. Send ₹20,000 to..." [!] | ● INTENT_DETECTED:       MONEY_TRANSFER       |
|                                    | ● TACTIC_DETECTED:       URGENCY / PRESSURE   |
+------------------------------------+----------------------------------------------+
| ATTACK LAB CONTROL PANEL           | INCIDENT AUDIT TRAIL                         |
| Generator: [ Coqui XTTS v2   v ]   | ID        Time       Risk   Status   Action  |
| Target:    [ Trusted Contact v ]   | #INC-802  14:02:15   94     CRITICAL Terminated |
| [ GENERATE & SIMULATE ATTACK ]     | #INC-801  13:45:01   12     SAFE     Passed  |
+------------------------------------+----------------------------------------------+
```
