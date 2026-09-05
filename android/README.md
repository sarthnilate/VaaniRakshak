# 📱 VaaniRakshak — Standalone Android Mobile Application

**Package Name:** `com.vaanirakshak.security`  
**Target SDK:** Android 14 (API Level 34)  
**Min SDK:** Android 8.0 (API Level 26)  
**Language & UI Framework:** Kotlin + Jetpack Compose + Material 3  
**Networking:** Ktor Client (WebSocket Streaming + REST API)  

---

## 📌 Mobile App Architecture & Key Features

1. **Telecom CallScreeningService (`VaaniCallScreeningService.kt`)**:
   - Extends official Android Telecom `CallScreeningService` API to intercept incoming/outgoing telephony calls in real time.
   - Evaluates incoming caller CLI against trusted contacts and dispatches audio feature streams to the VaaniRakshak backend.

2. **Real-time PCM Audio Streamer (`CallStreamManager.kt`)**:
   - Streams 16kHz 16-bit PCM audio chunks over WebSocket directly to the backend engine for sub-300ms anti-spoofing and intent evaluation.

3. **System Alert Overlay HUD (`EmergencyInterventionOverlay.kt` & `MinimalSecurityBadgeHUD.kt`)**:
   - Displays real-time risk score badge (0–100) over active calls.
   - Triggers full-screen red intervention HUD during high/critical scam threats (risk score ≥ 90).

4. **Speaker Biometric Enrollment (`SpeakerEnrollmentScreen.kt`)**:
   - Voice identity registration UI capturing 10-second enrollment audio samples to generate ECAPA-TDNN embeddings in the encrypted profile vault.

5. **Post-Call Incident Explanation (`PostCallExplanationScreen.kt`)**:
   - Displays post-call breakdown, forensic evidence summary, and single-tap reporting to the 1930 National Cyber Crime Portal.

---

## 🛠️ How to Build & Run in Android Studio

### Prerequisites
- **Android Studio** (Hedgehog 2023.1.1 or later / Iguana / Jellyfish)
- **JDK 17** (Configured as Gradle JDK)
- **Android Device or Emulator** running Android 8.0+ (API Level 26+)

### Step-by-Step Instructions
1. **Open Project:**
   - Launch Android Studio.
   - Select **Open** and navigate to the `android/` folder inside `VaaniRakshak`:
     `/Users/sarthnilate/Documents/VaaniRakshak/android`
2. **Sync Gradle:**
   - Allow Gradle to sync dependencies (`Ktor`, `Jetpack Compose`, `Material3`).
3. **Connect Backend Server:**
   - Ensure the VaaniRakshak backend is running (`./run_backend.sh`).
   - For Android Emulator: Backend URL points to `http://10.0.2.2:8000`.
   - For Physical Device: Update backend IP in `CallStreamManager.kt` to your laptop's local LAN IP (e.g., `http://192.168.x.x:8000`).
4. **Run App:**
   - Select target emulator/device and click **Run 'app'** (`Shift + F10`).
