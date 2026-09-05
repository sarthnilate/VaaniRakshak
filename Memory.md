# Memory.md

Real implementation state. Updated after every completed phase, per
Rules.md section 16 and README.md's recommended workflow. Nothing in this
file is aspirational — only what was actually done and actually verified.

---

## Phase 0 — Project Foundation

**Status: COMPLETE**

### What was built

1. **Monorepo skeleton** matching `Architecture.md` section 4 exactly:
   `android/`, `backend/`, `ml/`, `attack_lab/`, `datasets/`, `dashboard/`,
   `models/`, `experiments/`, `docs/`, `docker/`, `scripts/`, plus the five
   governing docs at repo root (`PRD.md`, `Architecture.md`, `Rules.md`,
   `Phases.md`, `Design.md`).

2. **Backend gateway (FastAPI)** — `backend/`
   - `app/main.py` — app entrypoint, mounts `api_router` under `/v1`.
   - `app/config.py` — `pydantic-settings`-based config, all values from
     env, safe non-secret local defaults only.
   - `app/api/health.py` — `GET /v1/health` (liveness) and
     `GET /v1/health/ready` (reports Redis + Postgres reachability without
     failing startup if they're down).
   - `db/session.py` — async SQLAlchemy engine/session factory + `ping_database()`.
   - `services/redis_client.py` — async Redis client factory + `ping_redis()`.
   - Structural placeholders (docstring-only `__init__.py`, no logic) for
     `app/auth`, `app/calls`, `app/websocket`, `app/risk`, `app/incidents`,
     `app/settings`, `workers/`, `schemas/` — each annotated with which
     future phase owns it. Deliberately empty; do not add logic here
     before that phase starts.
   - `tests/test_health.py` — 3 tests: root responds, liveness returns
     exact expected shape, readiness returns the expected key shape
     regardless of dependency status.
   - `requirements.txt` (core API deps only) and `requirements-ml.txt`
     (heavy ML deps, commented out — introduced starting Phase 3 so the
     Phase 0 gateway image stays light).
   - `Dockerfile` with a `HEALTHCHECK` hitting `/v1/health`.

3. **Dashboard shell (React + TS + Vite + Tailwind)** — `dashboard/`
   - Minimal `App.tsx` + `HealthStatus.tsx` that calls the backend's
     `/v1/health/ready` and renders dependency status. This is a Phase 0
     placeholder only — the real Live Security Command Center navigation
     and screens (Design.md section 8) are Phase 12 work.
   - Tailwind configured with the semantic status colors from
     Design.md section 3 (`safe`/`low`/`medium`/`high`/`critical`) —
     present as tokens only, not yet used for real risk data.
   - `Dockerfile` with a `HEALTHCHECK` on port 5173.

4. **Docker Compose** (`docker-compose.yml`) — four services, each with a
   `healthcheck`: `redis` (redis-cli ping), `postgres` (pg_isready),
   `backend` (curl `/v1/health`), `dashboard` (wget `/`). `backend` and
   `dashboard` `depends_on` their prerequisites with `condition:
   service_healthy` where applicable.

5. **`.env.example`** at repo root — every config key the backend/dashboard
   currently read, all placeholder values, no real secrets. `.gitignore`
   excludes `.env`, `node_modules/`, Python caches, Android build output,
   model checkpoints, and raw dataset audio (only `.gitkeep` placeholders
   are tracked under `datasets/*/` and `models/checkpoints/`,
   `models/registry/`).

6. **`docs/` stubs** — `DATASET_CARD.md`, `MODEL_CARD.md`, `TRAINING.md`,
   `LANGUAGE_COVERAGE_MATRIX.md`, `SIH_DEMO.md` created as explicit
   "NOT YET POPULATED" documents naming which phase populates them. No
   fabricated numbers, languages, or results anywhere in them
   (Rules.md section 18).

7. **`README.md`** — governing-doc index, repo layout summary, exact local
   dev commands (with and without Docker), and an explicit "what Phase 0
   does NOT include" section so nobody mistakes the skeleton for finished
   work.

### Tests run and actual results

```
$ cd backend && pip install -r requirements.txt   # succeeded, no errors
$ cd backend && pytest -q
...                                                                      [100%]
3 passed, 1 warning in 0.64s
```

The one warning is a `pytest-asyncio` deprecation notice about an unset
fixture loop scope config — cosmetic, not a failure.

`docker compose` itself was **not** executed — this sandbox has no Docker
daemon available. Instead, `docker-compose.yml` was validated by parsing it
as YAML (`yaml.safe_load` succeeded). The dashboard's `npm install` was
**not** run in this session either (no verification of the exact resolved
dependency tree yet) — flagged below as a follow-up, not silently assumed
to work.

### Architectural decisions made in this phase

- Split `requirements.txt` (core API) from `requirements-ml.txt` (heavy ML,
  currently all commented out) so the Phase 0 backend container stays small
  and boots without GPU/ML dependencies. This isn't in Architecture.md
  explicitly but doesn't contradict it — flagging here per Rules.md
  section 16 item 4 ("do not rewrite... without a reason", and per the
  master prompt: explain any deviation and record it).
- `/v1/health/ready` reports dependency status in its response body rather
  than failing the HTTP call, so the endpoint itself always answers (the
  gateway process is up) while still surfacing degraded dependencies for
  observability — matches the "AI failure must degrade safely, don't
  fabricate a SAFE result" spirit of Rules.md section 11, applied here to
  infra health rather than ML.

### Known limitations / honest gaps

- No Android project has been created yet — `android/` only has the
  directory skeleton from Architecture.md section 4. Phase 9 owns this.
- No database schema/migrations exist. `db/session.py` can connect and
  ping but there are no tables yet (Rules.md's list of core tables in
  Architecture.md section 9 is not yet implemented).
- No ML code, no Attack Lab generation logic, no WebSocket streaming.
  These are Phases 1, 3–8, and 11 respectively.
- `docker compose up` has not actually been run end-to-end in this
  environment (no Docker daemon here). The compose file is believed
  correct (valid YAML, service definitions mirror the working backend
  Dockerfile and dashboard Dockerfile) but should be run once in an
  environment with Docker before treating it as fully verified.
- Dashboard dependencies (`npm install`) have not been installed/verified
  in this session.

### Exact commands to reproduce current state

```bash
cd backend
pip install -r requirements.txt
pytest -q                      # expect: 3 passed

cd ../dashboard
npm install                    # not yet verified in this session
npm run build                  # not yet verified in this session

cd ..
python3 -c "import yaml; yaml.safe_load(open('docker-compose.yml')); print('valid')"
```

### Blockers

None for Phase 0 itself. Before Phase 1 (Attack Lab Foundation) starts,
someone should run `docker compose up --build` once in a real Docker
environment to confirm the four services actually reach `healthy` state
together — that was not possible in this sandbox (no Docker daemon, and
network egress is restricted to package registries, not arbitrary Docker
Hub pulls in this particular execution environment).

### Next phase

**Phase 1 — Attack Lab Foundation** (Phases.md): Attack Lab UI, consent
workflow, reference voice manager, language selector, script manager,
generator adapter interface, synthetic sample metadata, sample browser,
demo playback, provenance storage. Depends on nothing from Phase 0 beyond
the repo skeleton and the `attack_lab/` directories already in place.
