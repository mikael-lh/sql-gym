# Phase 6 implementation plan

## Status

**Approved** (2026-07-18). Linear epic + per-milestone issues to be created next; implementation proceeds per `.cursor/rules/workflow.mdc`.

## Source

- PRD: `prd/phase-6-reliability-and-code-quality.md` (approved 2026-07-18)
- Proposed Linear epic: **TIM-___** _(create after plan approval)_
- Proposed child issues: one per milestone below _(numbers assigned when created)_

## Resolved product decisions (2026-07-18)

| Topic | Decision |
|-------|----------|
| **Missing `SESSION_SECRET` in production** | **Hard-fail:** the app refuses to start in production without a real secret. |
| **PR sizing** | **Small, focused PRs** — one main concern each. |
| **Scope** | **Full PRD scope** (R1–R11); nothing trimmed. |
| **"Production" detection** | Explicit `APP_ENV` env var (`development` default; `production` triggers the secret check). Confirmed 2026-07-18. |
| **PRD/README status flip** | Handled by a separate **`update-prd`** pass after milestones merge — **not** in M10. Confirmed 2026-07-18. |

## Guiding constraints

- **No user-visible behavior change**, with one intended exception: Milestone 1 (R2) fixes valid `SELECT`s being wrongly rejected.
- Reuse existing modules and patterns; do not introduce new frameworks.
- Every milestone is an independently reviewable, independently testable PR.
- `./scripts/validate-env.sh` (build, ruff, mypy, pytest) stays green on every milestone.

## Ordering rationale

Sequenced lowest-risk / highest-value first, per the PRD's suggested order:

```text
M1 (R2)  → M2 (R7)  → M3 (R3)  → M4 (R1)  → M5 (R4)  → M6 (R5)
        → M7 (R8)  → M8 (R9)  → M9 (R10 + R6)  → M10 (R11 docs/closeout)
```

Dependency notes:
- **M4 (pooling) depends on M1 (read-only execution)** because both touch `execute_query`; M4 must preserve M1's read-only guarantee and reset connection state between pool checkouts.
- **M9 (JS split) absorbs R6** (extract one shared `formatTime` helper while splitting the file).
- M10 (docs) runs last so wording matches the shipped code.

---

## Milestones

### M1 — R2: Database-enforced read-only execution + fix false rejections

**Goal:** Make "read-only only" a guarantee enforced by PostgreSQL, and stop wrongly blocking valid `SELECT`s whose text/strings contain keywords or semicolons.

**Files to create or modify:**
- `src/app/execution/execute.py` — run each query in a **read-only transaction** (e.g. set `conn.read_only = True` / `SET default_transaction_read_only = on` before executing); relax the raw-text guards.
- `src/app/execution/sql_sanitize.py` — keep comment stripping; the light text check becomes UX-only ("enter a query"; "must be a SELECT/WITH query"), no longer the safety mechanism.
- `tests/test_execution.py`, `tests/test_sql_sanitize.py` — add cases below.

**Implementation notes:**
- Write protection comes from the read-only transaction, independent of `DATABASE_URL` pointing at the `sql_gym_readonly` role (defense in depth kept).
- Drop the forbidden-keyword regex and the raw-text semicolon check that produce false positives. A second statement that is also a `SELECT` is harmless under a read-only transaction; any write is rejected by the database. Keep a minimal "looks like a SELECT/WITH" prefix check only for a friendly upfront message.
- Statement timeout and 500-row limit unchanged.

**Acceptance criteria covered:** R2 (all).

**Tests / checks:**
- `DELETE`/`UPDATE`/`DROP` rejected by the read-only transaction (test proves it even if the text check is bypassed).
- `SELECT ... WHERE headline = 'plans to create jobs'` returns rows (no false rejection).
- `SELECT` with a semicolon inside a quoted string runs successfully.
- Existing SELECT-only behavior for genuinely empty/non-SELECT input preserved; ruff, mypy, pytest green.

**Risks:** Low–medium. Verify read-only mode actually blocks writes on the target PG role in a test; confirm psycopg transaction semantics (autocommit vs. explicit transaction).

---

### M2 — R7: Remove leftover dead code

**Goal:** Delete code that the running app no longer uses, plus the tests that only exist to cover it.

**Files to remove (after confirming each is unused by the running app):**
- `static/js/practice-timer.js` (no template loads it).
- `src/app/workspace/navigation.py` → `resolve_workspace_exercise`.
- `src/app/progress/navigation.py` → `continue_exercise_url` (and its export in `src/app/progress/__init__.py`).
- `src/app/domain/progress.py` → `ProgressSummary`, `ProgressMetric`, `build_progress_summary`, `DEMO_PROGRESS`.
- `src/app/domain/attempts.py` → `Attempt`, `DEMO_ATTEMPT` (whole module if fully unused).
- `src/app/domain/grading.py` → `GRADING_PLACEHOLDER`.
- `src/app/domain/exercises.py` → `TIMES_ARCHIVE_PLACEHOLDER_EXERCISE`.
- `src/app/domain/datasets.py` → `TIMES_ARCHIVE_DEMO_DATASET`; delete unused fixture `src/app/fixtures/times/archive_articles_demo.json` (keep provenance references coherent).
- `static/styles.css` — rules tied only to removed elements (e.g. `.editor-form`).
- Corresponding tests in `tests/test_domain.py`, `tests/test_progress_navigation.py`, etc., that only exercised removed symbols.

**Implementation notes:**
- Before deleting each symbol: grep `src/`, `templates/`, `static/`, `scripts/` to confirm no runtime import. If any item turns out to be used, keep it and note it in the PR.
- Deletion-only PR (one concern). If it feels large, split into "backend dead code" and "frontend dead code (JS + CSS)".

**Acceptance criteria covered:** R7 (all).

**Tests / checks:** `uv run pytest` green after test removals; ruff `F401`/unused-import clean; grep confirms no dangling references.

**Risks:** Low; purely subtractive. Main risk is deleting something still referenced — mitigated by the grep gate.

---

### M3 — R3: Single signing-secret source + hard-fail in production

**Goal:** One place defines the signing secret; the app refuses to start in production without `SESSION_SECRET`.

**Files to create or modify:**
- `src/app/db/settings.py` (or a small `src/app/config.py`) — add `get_session_secret()` and `get_app_env()`; the dev fallback lives here only.
- `src/app/main.py` — import the shared accessor; on app creation, if `APP_ENV == "production"` and `SESSION_SECRET` is unset/empty, raise a clear startup error.
- `src/app/progress/cookie.py` — replace its local `_session_secret()` with the shared accessor.
- `.env.example` — document `APP_ENV` and clarify `SESSION_SECRET` is required in production.
- `tests/test_db_settings.py` (or new `tests/test_config.py`) — cover: dev fallback works; production without secret raises; production with secret works.

**Implementation notes:**
- Default `APP_ENV=development` so local dev and existing tests are unaffected.
- Keep the dev fallback string in exactly one location.

**Acceptance criteria covered:** R3 (all).

**Tests / checks:** startup-guard tests above; existing session/progress-cookie tests still pass; ruff, mypy.

**Risks:** Low. Ensure the guard runs at app startup, not import time, so tooling that imports modules isn't blocked.

---

### M4 — R1: Reuse database connections (connection pool)

**Goal:** Replace per-query `psycopg.connect(...)` with a shared pool created at startup and closed at shutdown.

**Files to create or modify:**
- `pyproject.toml` — add `psycopg_pool` dependency; `uv.lock` updated via `uv lock`.
- `src/app/execution/execute.py` — borrow a connection from the pool; preserve M1's read-only transaction and reset connection state between checkouts.
- `src/app/main.py` — create the pool in a FastAPI lifespan handler; close on shutdown. Handle "no `DATABASE_URL`" gracefully (no pool; keep today's "database unavailable" message).
- `tests/test_execution.py` — concurrency test (multiple queries reuse the pool, no connection exhaustion); unavailable-DB path still returns the friendly error.

**Implementation notes:**
- Small pool size with sensible min/max; statement timeout still applied per query.
- The pool must not leak read/write state between uses — set read-only per checkout or reset on return.

**Acceptance criteria covered:** R1 (all).

**Tests / checks:** concurrency test; timeout + 500-row limit unchanged; ruff, mypy, pytest; `uv build`.

**Risks:** Medium — connection lifecycle and test setup (needs a live PG or a mock). Confirm behavior when `DATABASE_URL` is absent (CI without DB).

---

### M5 — R4: One place that serializes results/errors/grading

**Goal:** Remove the duplicated serializers across `api/practice.py` and `practice_session.py`.

**Files to create or modify:**
- `src/app/api/serializers.py` _(new, or a shared helper module)_ — single `serialize_query_result(result, *, row_limit=None)`, `serialize_execution_error(...)`, `serialize_grading(...)`.
- `src/app/api/practice.py`, `src/app/practice_session.py` — import the shared functions; the 25-row session preview becomes `row_limit=SESSION_PREVIEW_ROW_LIMIT`.
- `tests/test_practice_api.py`, `tests/test_practice_session.py` — assert full results vs. 25-row previews are unchanged.

**Acceptance criteria covered:** R4 (all).

**Tests / checks:** existing API and session tests pass unchanged; ruff, mypy.

**Risks:** Low. Preserve the exact `run` vs. non-run `postgres_message` behavior currently in both copies.

---

### M6 — R5: Single source of truth for progress labels

**Goal:** Define status→label once server-side; the browser uses the server-provided label.

**Files to create or modify:**
- `src/app/domain/progress.py` (or `progress/__init__.py`) — one `PROGRESS_LABELS` map + accessor.
- `src/app/api/practice.py`, `src/app/workspace/context.py` — import the shared map (remove local `_PROGRESS_LABELS` copies).
- `static/js/practice-workspace.js` — use `progress.label` from payloads; remove the JS `progressLabelForStatus` fallback (or keep a minimal guard only).
- `tests/` — assert label text in API payloads unchanged.

**Acceptance criteria covered:** R5 (all).

**Tests / checks:** badge/status text identical to today (API tests + a browser/layout check if warranted); ruff, mypy.

**Risks:** Low. Ensure every payload that the client renders actually includes `label`.

---

### M7 — R8: Simplify route wiring

**Goal:** Reduce pass-through wrappers in `main.py` and de-duplicate the 404 rendering.

**Files to create or modify:**
- `src/app/main.py` — register `api_*` handlers directly and/or move API routes into an `APIRouter` (e.g. `src/app/api/routes.py`); add a small `render_not_found(request)` helper for the repeated 404 `TemplateResponse`.
- `tests/test_workspace_routes.py`, `tests/test_practice_api.py`, `tests/test_app.py` — unchanged expectations (same URLs, responses, status codes).

**Acceptance criteria covered:** R8 (all).

**Tests / checks:** all route tests pass with identical status codes/bodies; fewer lines in `main.py`; ruff, mypy.

**Risks:** Low–medium. Keep FastAPI response types and tags equivalent so the OpenAPI schema and tests don't drift.

---

### M8 — R9: Typed workspace context

**Goal:** Replace the loose ~40-key `dict[str, object]` with a typed structure and drop duplicated top-level vs. nested values.

**Files to create or modify:**
- `src/app/workspace/context.py` — introduce a Pydantic model / dataclass for the workspace context; `get_workspace_context` returns it (with a `.model_dump()`/mapping for the template + `workspace_config`).
- `src/app/api/practice.py` — consume typed fields instead of string-keyed indexing (`context["exercise"]` → `context.exercise`).
- `templates/workspace.html` — adjust only if key access paths change (aim to keep template variables stable).
- `tests/test_workspace_context_*.py` — assert the same rendered content and API payloads.

**Acceptance criteria covered:** R9 (all).

**Tests / checks:** workspace + API render identical content; mypy would now catch a missing/renamed field; ruff, pytest.

**Risks:** Medium — touches both the template contract and the API. Keep template variable names stable to minimize churn.

---

### M9 — R10 (+ R6): Split the workspace JavaScript into modules

**Goal:** Break `static/js/practice-workspace.js` (~830 lines) into focused ES modules, and extract one shared `formatTime` helper (R6), with no behavior change.

**Files to create or modify:**
- `static/js/workspace/` _(new)_ — e.g. `render.js`, `stopwatch.js`, `navigation.js`, `api-client.js`, `format.js` (shared `formatTime`).
- `static/js/practice-workspace.js` — becomes a thin orchestrator importing the modules; `practice-workspace-entry.js` unchanged.
- `tests/` — existing browser/layout tests (`test_workspace_*`, `tests/playwright_layout.py`) exercise the same flows.

**Implementation notes:**
- Pure refactor: move functions, wire imports/exports; keep DOM ids and behavior identical.
- Replace the three inline `M:SS` formatters with the shared `formatTime` (R6).

**Acceptance criteria covered:** R10 (all), R6 (all).

**Tests / checks:** run, submit, switch, drawer, timer, and modal behave identically; browser/layout tests pass.

**Risks:** Medium — ES module load order and the `globalThis.resetPracticeEditor` interop with the CodeMirror bundle. Verify in a browser smoke test.

---

### M10 — R11: Docs, manual test plan, validation, PRD closeout

**Goal:** Make docs match the cleaned-up code and record the phase outcome.

**Files to create or modify:**
- `README.md`, `docs/session-state.md` — update wording where clean-up changed structure (execution, config, JS layout).
- `docs/phase-6-manual-test-plan.md` _(new)_ — run/submit happy path, the R2 false-rejection fix, progress tracking, production-secret hard-fail check.
- `scripts/validate-env.sh` — phase banner if applicable.

**Note:** the Phase 6 **PRD/README status flip is out of M10** — it is handled by a separate `update-prd` pass after the milestones merge (resolved 2026-07-18).

**Acceptance criteria covered:** R11 (all) + phase-level AC checklist closeout.

**Tests / checks:** `./scripts/validate-env.sh`, full `uv run pytest`, ruff, mypy.

**Risks:** None significant.

---

## Requirement coverage

| PRD requirement | Milestone(s) |
|-----------------|--------------|
| R1. Connection pooling | M4 |
| R2. Read-only execution + false-rejection fix | M1 |
| R3. Secret hard-fail + de-dup | M3 |
| R4. One serializer source | M5 |
| R5. One progress-label source | M6 |
| R6. Frontend time-format helper | M9 |
| R7. Remove dead code | M2 |
| R8. Simplify route wiring | M7 |
| R9. Typed workspace context | M8 |
| R10. Split large JS file | M9 |
| R11. Docs, test plan, validation | M10 |

Every PRD phase-level acceptance-criteria checkbox maps to the milestone(s) above (R1→M4, R2→M1, R3→M3, R4/R5/R6→M5/M6/M9, R7→M2, R8/R9/R10→M7/M8/M9, R11→M10).

## Out of scope (explicit)

- New learner-facing features, datasets, exercises, or screens.
- Changing grading rules or the strict grid-match logic.
- Live schema introspection (schema still comes from the checked-in fixture).
- Visual/design redesign.
- Performance work beyond connection pooling.
- Framework/language changes.

## Engineering principles check

| Principle | Assessment |
|-----------|------------|
| Minimal scope per PR | Ten milestones, one concern each; deletions (M2) and refactors (M7–M9) kept separate from behavior changes (M1, M3, M4). |
| Design fit | Reuses existing modules (`execution`, `progress`, `workspace`, `api`); pool lives in app lifespan; config accessor beside existing `db/settings.py`. |
| Simplicity | Read-only transaction replaces brittle keyword scanning; shared helpers replace copies; no new frameworks. |
| DRY | M5 (serializers), M6 (labels), M9/R6 (time format) each collapse duplication to one source. |
| Less abstraction where over-engineered | M2 removes unused scaffolding; M9 splits an oversized file into readable units. |
| Tests | Each milestone lists targeted tests; validation suite green per milestone. |
| Style vs behavior | Refactor-only PRs (M2, M5–M9) assert unchanged behavior; behavior changes isolated to M1/M3/M4. |

**Non-blocking trade-offs / risks for user review:**
- M1 relaxes multi-statement/keyword text checks and leans on the read-only transaction for safety; this is a deliberate simplification (documented + tested).
- M4 requires a live PostgreSQL (or a mock) for the concurrency test; CI without a DB must still pass the "database unavailable" path.
- M9 is a pure JS refactor whose main risk is module-load/interop with the vendored CodeMirror bundle — covered by a browser smoke test.

## UI/layout review note

M6 and M9 touch `static/` (and possibly `templates/`) but are intended to be **no visual change**. Per `.cursor/rules/workflow.mdc` and `docs/ui-layout-review.md`, any milestone whose diff touches templates/styles/learner-visible chrome still runs `sql-gym-pre-review` (desktop + mobile viewport checks) before handoff.

## Suggested implementation order

```text
M1 → M2 → M3 → M4 → M5 → M6 → M7 → M8 → M9 → M10
```

M2 (dead code) and M3 (secret) are independent of M1 and can be reordered if preferred; M4 must follow M1.

## Open items for the user

- ~~Confirm `APP_ENV` as the production signal.~~ **Resolved 2026-07-18:** use `APP_ENV`.
- ~~Confirm whether PRD/README status flips happen in M10 or via `update-prd`.~~ **Resolved 2026-07-18:** via a separate `update-prd` pass after milestones merge.

## Approval

- [x] User approves this implementation plan (2026-07-18).
- [ ] Create Linear epic and one child issue per milestone (M1–M10), each linking `prd/phase-6-reliability-and-code-quality.md` + acceptance criteria.
- [ ] Begin implementation with **`sql-gym-implement-issue`** (or **`sql-gym-run-phase`** if autonomous execution is authorized).
