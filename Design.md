# VaaniRakshak — Design System

## 1. Design Direction

VaaniRakshak should feel like:

**premium Android security + modern AI command center + Indian civic technology**

Not:

- generic banking app
- cartoonish AI app
- hacker-themed interface
- over-decorated dashboard

The product should communicate:

**calm → intelligent → trustworthy → urgent when necessary**

---

## 2. Brand

Name:

**VaaniRakshak**

Meaning:

- Vaani = voice
- Rakshak = protector

Suggested product line:

**Protect the voice. Verify the intent. Stop the threat.**

---

## 3. Theme

Primary:

- deep neutral/navy security background
- clean surfaces
- high-contrast text

Status colors:

- SAFE → green
- LOW → neutral/blue
- MEDIUM → amber
- HIGH → orange
- CRITICAL → red

Do not use status colors as decoration. They communicate semantic state.

---

## 4. Typography

Android:

- Material 3 typography
- Roboto/system font
- clear numerical emphasis for risk score

Dashboard:

- Inter or equivalent modern sans-serif
- monospace only for technical metrics/logs

Multilingual:

Use fonts with broad Unicode coverage and test:

- Devanagari
- Bengali
- Tamil
- Telugu
- Kannada
- Malayalam
- Gujarati
- Gurmukhi
- Arabic
- CJK
- Cyrillic
- Latin

Never assume one font covers every script correctly.

---

## 5. Android Call Security UI

The call UI should remain minimal.

Example:

```text
┌─────────────────────────────┐
│ 🛡 Protected      37/100    │
│ ███████░░░░░░░░░             │
└─────────────────────────────┘
```

Do not cover the caller's face/name or normal call controls.

Risk changes should be subtle.

Critical state becomes visually obvious:

```text
🛡 THREAT DETECTED
96 / 100
CRITICAL
```

---

## 6. Post-Call Explanation

Use a full-screen animated security report.

Hierarchy:

1. Decision
2. Risk score
3. Primary reason
4. Evidence
5. Recommended action

Example:

```text
🚨 CALL PROTECTED

96 / 100
CRITICAL

AI-generated voice      96%
Speaker similarity      92%
Impersonation           HIGH
Financial request       DETECTED
Urgency                 DETECTED

Why?
The voice resembles a trusted contact,
but synthetic speech indicators were strong
and the conversation requested money urgently.

Recommended:
Verify through a trusted channel.
```

---

## 7. Attack Lab UI

Clearly distinguish it from the real consumer security experience.

Header:

`ATTACK LAB — CONTROLLED DEMONSTRATION`

Banner:

`CONSENTED / SYNTHETIC / RESEARCH MODE`

Sections:

- Reference Voice
- Language
- Script
- Generator
- Generated Sample
- Detection Result
- Export Evidence

Use warning styling but do not make it look malicious or game-like.

---

## 8. Dashboard

### Layout

Left navigation:

- Overview
- Live Protection
- Incidents
- Attack Lab
- Dataset Explorer
- Models
- Languages
- Evaluations
- Settings

Main content:

Large live risk card.

Secondary cards:

- Synthetic probability
- Speaker similarity
- Threat level
- Intent
- Social engineering
- latency

Bottom:

Risk timeline + evidence.

---

## 9. Risk Timeline

Show:

```text
0s   10
2s   21
4s   39
6s   61
8s   78
10s  94
```

Animate the line/bar smoothly.

Do not animate values faster than actual backend events.

---

## 10. Data Visualization

Prefer:

- line charts
- progress bars
- compact cards
- evidence chips
- timeline markers

Avoid:

- excessive pie charts
- 3D charts
- meaningless animations
- neon cyberpunk effects

---

## 11. Accessibility

Support:

- large text
- high contrast
- screen-reader labels
- color + text, never color alone
- touch targets appropriate for Android
- multilingual text expansion

---

## 12. Motion

Motion should explain state.

Use:

- smooth risk transitions
- subtle pulse for active protection
- decisive transition for critical state
- staged post-call explanation

Avoid:

- constant particle effects
- distracting gradients
- excessive bounce animations

---

## 13. SIH Visual Moment

The judge should be able to look at the phone and immediately understand:

```text
VOICE IMPERSONATION
        ↓
RISK RISING
        ↓
CRITICAL
        ↓
CALL PROTECTED
```

The animation should be memorable but credible.
