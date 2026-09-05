# VaaniRakshak

**SIH26104 — AI-Powered Real-Time Detection and Prevention of Voice Cloning Impersonation Attacks**

VaaniRakshak is a privacy-first, real-time voice-threat detection and
prevention platform for Android, built alongside a strictly controlled
Attack Lab used only for consented research and demonstration.

Governing documents (read in this order):

1. [`PRD.md`](./PRD.md) — product requirements and vision
2. [`Architecture.md`](./Architecture.md) — system architecture and repo layout
3. [`Rules.md`](./Rules.md) — engineering, AI, security and privacy rules
4. [`Phases.md`](./Phases.md) — implementation sequence
5. [`Design.md`](./Design.md) — visual design system
6. `Memory.md` — real implementation state, created/updated as phases complete

## Current status

**Phase 0 — Project Foundation: complete.** See `Memory.md` for the exact
state, what was verified, and what Phase 1 depends on.

## Repository layout

See `Architecture.md` section 4 for the full rationale. Top level:

```text
android/       Kotlin/Compose client (thin — screening, security UI, network)
backend/       FastAPI gateway, risk/decision services, DB/Redis access
ml/            Voice authenticity, speaker verification, STT, conversation,
               temporal and risk-fusion research code
attack_lab/    Controlled, consent-based synthetic-voice research/demo tool
datasets/      Manifests and provenance (raw audio is git-ignored)
dashboard/     React/TS/Vite/Tailwind judge-facing command center
models/        Checkpoints and a model registry (git-ignored contents)
docs/          Dataset/model cards, language coverage, demo & judge docs
docker/        Supporting Docker assets
scripts/       Dev/ops scripts
```

## Local development (Phase 0 slice)

Requires Docker and Docker Compose.

```bash
cp .env.example .env
docker compose up --build
```

This brings up:

| Service    | URL                            | Health check                     |
|------------|---------------------------------|-----------------------------------|
| backend    | http://localhost:8000          | `GET /v1/health`, `/v1/health/ready` |
| dashboard  | http://localhost:5173          | HTTP 200 on `/`                  |
| redis      | localhost:6379                 | `redis-cli ping`                 |
| postgres   | localhost:5432                 | `pg_isready`                     |

### Running the backend without Docker

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

```bash
cd backend
pytest
```

### Running the dashboard without Docker

```bash
cd dashboard
npm install
npm run dev
```

## What Phase 0 deliberately does NOT include

Per `Phases.md`, Phase 0 is documentation + a booting skeleton only. There is
no ML inference, no Attack Lab generation, no Android app, no WebSocket risk
streaming, and no real database schema yet — those arrive in the phases that
own them. Directories for those systems exist now (per `Architecture.md`)
but are intentionally empty/placeholder so the layout never has to be
rewritten later.

## Rules that apply to every contribution

- Never fabricate benchmark results, dataset provenance, or Android
  capabilities (`Rules.md` section 1, section 18).
- No secrets committed — `.env` is git-ignored, only `.env.example` is
  tracked (`Rules.md` section 12).
- No raw sensitive audio retained or logged by default (`Rules.md` section 9).
- The Attack Lab is consent-only and never a covert impersonation tool
  (`Rules.md` section 4).
