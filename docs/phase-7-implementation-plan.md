# Phase 7 implementation plan

## Status

**Awaiting approval** (2026-07-27). No application code until this plan is approved.

## Source

- PRD: `prd/phase-7-local-llm-explain-on-fail.md` (approved and active 2026-07-27)
- Proposed Linear epic: **TIM-___** _(create after plan approval)_
- Proposed child issues: one per milestone below _(numbers assigned when created)_

## Resolved product decisions (from PRD + this plan)

| Topic | Decision |
|-------|----------|
| **Learner job** | Explain a **failed** submit only. |
| **When** | After failed submit only (no standing Ask AI). |
| **Runtime** | Native **Ollama** over HTTP (default `http://127.0.0.1:11434`). |
| **Unavailable** | Clear **AI unavailable** message (reason class). |
| **Grading truth** | Strict grid match unchanged; AI never sets pass/fail. |
| **Session end** | **App process shutdown** (uvicorn lifespan `finally`) — not browser tab close. |
| **Cleanup timing** | Remove configured model on shutdown; **not** per explain request. |

### Open questions resolved in this plan (confirm or adjust)

| Topic | Recommendation |
|-------|----------------|
| **UI chrome** | Keep the existing grading modal. On **failed** submit only, show an **“Explain with AI”** button under the summary. Click loads explanation into the modal (loading → text or unavailable). Passed modal unchanged (no button). |
| **Context pack** | Send: exercise title, prompt, difficulty, `output_requirements`, learner SQL, `grading.summary`, and **expected column names only**. **Do not** send expected row values, full grids, or `reference_sql` (avoids spoiling the answer). |
| **Default model** | `llama3.2:3b` (small; override via env). |
| **Auto-pull** | **Yes** on first explain in the app process if the model is missing (may be slow). Track that this process pulled/used the model for shutdown cleanup. |
| **Cleanup opt-out** | Env `OLLAMA_KEEP_MODEL=1` skips delete on shutdown (frequent local dev). Default: cleanup **on**. |
| **Workers** | Document **single-worker** local assumption (`uvicorn` without multiple workers). Multi-worker pull/rm races out of scope. |

## Guiding constraints

- Prefer existing patterns: env helpers in `src/app/db/settings.py`, FastAPI lifespan in `src/app/main.py`, practice `APIRouter` in `src/app/api/routes.py`, grading modal in `static/js/workspace/render.js`.
- New outbound HTTP: use **httpx** (already a dependency; currently tests-only).
- Every milestone is a small, independently testable PR.
- `./scripts/validate-env.sh` stays green; Ollama tests **mock** by default / skip when unreachable.
- No cloud LLM providers; no partial-credit grading.

## Ordering rationale

```text
M1 (Ollama client + settings + shutdown cleanup)
  → M2 (explain API + safe context pack)
  → M3 (fail-modal UI + Playwright)
  → M4 (docs / manual test plan / validate-env banner)
```

- **M1 before M2:** API needs a client and pull/delete semantics.
- **M2 before M3:** UI calls a stable JSON endpoint.
- **Cleanup in M1:** lifespan hook lands with the client; M2/M3 only mark “model used this process.”
- **M4 last:** docs match shipped behavior.

---

## Milestones

### M1 — Ollama client, settings, and shutdown cleanup

**Goal:** Configurable native Ollama access; pull/chat/delete helpers; remove model on app shutdown unless opted out.

**Files to create or modify:**
- `src/app/db/settings.py` — `get_ollama_base_url()`, `get_ollama_model()`, `get_ollama_keep_model()`, optional timeout helper.
- `src/app/ai/` _(new)_ — e.g. `ollama.py` (httpx client: health/tags, pull, chat, delete), `session.py` or module flags for “model used this process.”
- `src/app/main.py` — in lifespan `finally`, after `close_pool()`, call cleanup (best-effort; never raise out of shutdown).
- `.env.example` — `OLLAMA_BASE_URL`, `OLLAMA_MODEL`, `OLLAMA_KEEP_MODEL`.
- `tests/test_ollama_client.py` _(new)_ — mock httpx; cleanup skipped when keep-model / unused / Ollama down.

**Implementation notes:**
- Defaults: base `http://127.0.0.1:11434`, model `llama3.2:3b`, keep-model false.
- Cleanup deletes **only** the configured model name, and **only** if this process marked it used (or pulled) — avoid deleting unrelated user models if we never touched AI.
- Log cleanup failures; do not fail process exit.
- Single-worker assumption documented in module docstring / README (M4).

**Acceptance criteria covered:** A2 (client foundation), A4 (cleanup), part of A5 (env).

**Tests / checks:** unit tests with mocked transport; lifespan test pattern like `test_execution_pool.py`; ruff, mypy, pytest.

**Risks:** Medium — first real outbound HTTP; Ollama API details (pull streaming, delete path). Pin to documented Ollama HTTP endpoints in code comments.

---

### M2 — Explain-on-fail API + safe context pack

**Goal:** `POST` endpoint that, for a failed grading context, returns explanation text or a structured unavailable error — without changing grading/progress.

**Files to create or modify:**
- `src/app/ai/explain.py` _(new)_ — build prompt/context pack; call Ollama chat; map failures to reason codes (`not_running`, `model_missing`, `timeout`, `error`).
- `src/app/api/practice.py` + `src/app/api/routes.py` — e.g. `POST /api/practice/{dataset_id}/{exercise_id}/explain` with body `{ "sql": "...", "grading_summary": "..." }` (and/or reuse server-side last attempt). Prefer **server-side** exercise lookup + last submit attempt from session when possible so the client cannot inject fake grading; if session lacks a failed attempt, return 409/422.
- `tests/test_explain_api.py` _(new)_ — mock Ollama; assert pass path not required; failed attempt → 200 `{ "explanation": "..." }` or 503/422 `{ "error": { "code": "ai_unavailable", "reason": "..." } }`; grading/progress endpoints unchanged.

**Implementation notes:**
- Endpoint is only meaningful after a failed submit; reject or no-op explain when last attempt passed / missing.
- Context pack per table above — no `reference_sql`, no expected rows.
- System prompt: tutor tone; do not reveal a full correct query; focus on mismatch summary + how to improve.
- Mark model-used flag when pull or successful chat runs (feeds M1 cleanup).
- Auto-pull once per process on first explain if model absent (timeouts → unavailable).

**Acceptance criteria covered:** A1 (server), A2, A3 (API shape), A4 (usage tracking).

**Tests / checks:** mocked httpx; no live Ollama required in CI; ruff, mypy, pytest.

**Risks:** Medium — prompt quality; spoiler leakage if context grows. Keep pack minimal; add a unit test that context builder excludes `reference_sql` / grid rows.

---

### M3 — Grading modal UI (Explain with AI)

**Goal:** On failed submit only, modal offers Explain with AI; shows loading, explanation, or AI unavailable; passed flow unchanged.

**Files to create or modify:**
- `templates/workspace.html` — modal region for explain button + status/explanation text (hidden by default).
- `static/js/workspace/render.js` — extend `createGradingModal` / show path: on `passed === false`, reveal Explain control; wire click → fetch explain API; render result or unavailable copy.
- `static/js/workspace/api-client.js` — `buildExplainUrl(...)`.
- `static/js/practice-workspace.js` — pass any needed handles (keep thin).
- `static/styles.css` — minimal styles for explain block (match existing modal; no redesign).
- `tests/test_grading_modal.py` and/or new `tests/test_explain_modal.py` — Playwright: fail modal shows Explain; stub explain JSON success and unavailable; pass modal has no Explain. Use `page.route` like existing submit stubs. Desktop + mobile viewports if layout of new controls is asserted (`docs/ui-layout-review.md`).

**Implementation notes:**
- Do **not** auto-call explain on every fail (avoids surprise pull/latency); button keeps A3 visible when user opts in.
- Dismiss (OK / Escape) still works during loading.
- No change to progress badge updates on submit.

**Acceptance criteria covered:** A1 (UX), A3 (UI).

**Tests / checks:** Playwright integration tests; layout matrix if new controls join a row group; ruff N/A for JS — manual/browser checks in PR.

**Risks:** Medium — UI/layout pre-review applies (`templates/` + CSS). Keep chrome inside the modal to limit layout surface.

---

### M4 — Docs, manual test plan, validation banner

**Goal:** Document Ollama setup, env vars, cleanup behavior; Phase 7 manual test plan; validate-env phase line.

**Files to create or modify:**
- `README.md` — Phase 7 behavior notes; env table; Ollama install pointer; single-worker note.
- `.env.example` — already seeded in M1; ensure docs match.
- `docs/session-state.md` — explain route + modal behavior.
- `docs/phase-7-manual-test-plan.md` _(new)_ — failed submit + explain; unavailable; cleanup on stop; keep-model flag.
- `scripts/validate-env.sh` — active phase banner → Phase 7.
- `prd/README.md` — point at this plan once approved (status: plan approved / implementing).

**Note:** Phase 7 **PRD complete status flip** is a later **`update-prd`** after milestones merge (same as Phase 6), not part of M4.

**Acceptance criteria covered:** A5; phase-level docs AC.

**Tests / checks:** `./scripts/validate-env.sh`; no live Ollama required.

**Risks:** Low.

---

## Requirement coverage

| PRD requirement | Milestone(s) |
|-----------------|--------------|
| A1. Explain failed submits | M2, M3 |
| A2. Native Ollama | M1, M2 |
| A3. AI unavailable | M2, M3 |
| A4. Cleanup on app session end | M1 (hook), M2 (usage flag) |
| A5. Docs + validation | M1 (`.env.example`), M4 |

Phase-level acceptance criteria map to the same milestones.

## Out of scope (explicit)

- Cloud LLMs / API keys for hosted providers.
- AI grading authority, partial credit, expected-grid changes.
- Pre-submit / always-visible Ask AI.
- Explain on **passed** submits.
- Dockerized Ollama as required setup.
- Cleanup on browser tab close alone.
- Multi-worker uvicorn pull/rm coordination.

## Engineering-principles check

| Principle | Plan fit |
|-----------|----------|
| Minimal scope / small PRs | Four milestones; one concern each |
| Design fit | Lifespan + settings + APIRouter + existing modal |
| Simplicity | httpx client; button-triggered explain; no new frontend framework |
| DRY | Shared Ollama client; one context builder |
| Tests with behavior | Mocked unit + Playwright with route stubs |
| No speculative abstraction | No provider plugin interface in Phase 7 |

Non-blocking trade-offs for review:
- Button vs auto-explain (plan chooses button).
- Auto-pull may download GBs on first click (documented; cleanup on exit).
- Default 3B model quality varies by machine — override via `OLLAMA_MODEL`.

## Risks and unknowns

- Ollama pull can be slow/large; UI must show loading and allow dismiss.
- Prompt may occasionally suggest overly complete SQL — mitigate via system prompt + no reference_sql in context.
- Cloud agents typically lack Ollama — unavailable path must be tested without a live server.

## Approval

- [ ] User approves this implementation plan (or requests adjustments).
- [ ] Create Linear epic + one child issue per milestone (M1–M4), each linking `prd/phase-7-local-llm-explain-on-fail.md` + acceptance criteria.
- [ ] Begin implementation with **`sql-gym-implement-issue`** (or **`sql-gym-run-phase`** if autonomous execution is authorized).

**No application code until this plan is approved.**
