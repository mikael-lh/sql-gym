# Phase 3 implementation plan

## Status

**Complete** — implemented via TIM-42, TIM-41, TIM-38, TIM-39, and TIM-40 (2026-06-09).

## Source

- PRD: `prd/phase-3-progress-and-timed-mode.md` (approved 2026-06-08)
- Linear epic: `TIM-37` _(proposed; create after plan approval)_
- Child issues: `TIM-38`, `TIM-39`, `TIM-40`, `TIM-41`, `TIM-42`

## Planning decisions

- **Progress cookie:** Name `sql_gym_progress`; signed with `SESSION_SECRET` via `itsdangerous` (same pattern as Starlette sessions); `HttpOnly`, `SameSite=Lax`, `max_age=5184000` (60 days), refreshed on each write.
- **Session unchanged:** `practice_attempts` stays in session cookie (browser-session scope) for draft SQL and last run/grade display.
- **Progress payload:** Versioned JSON, e.g. `{ "v": 1, "exercises": { "<id>": { "status": "passed"|"attempted", "passed_at": "<iso-utc>", "elapsed_seconds": <int|null> } } }`. No SQL or query results in cookie.
- **Progress writes:** Only on `POST …/submit` (after grading) and `POST /practice/progress/clear`. Not on `POST …/run` or GET pages.
- **Statuses:** `not_started` (absent from cookie), `attempted`, `passed` (sticky). Best `elapsed_seconds` = minimum on timed retries.
- **Continue link:** Next unpassed exercise in stable catalog order (`TIMES_ARCHIVE_CATALOG.exercises` tuple order). On `/practice`, if `difficulty` query param is set, continue within that difficulty only. Home uses full catalog.
- **Timed mode:** Client-side countdown in `static/js/practice-timer.js` for `exercise.mode == "Timed"` only. Duration = `estimated_time_minutes * 60`. Explicit **Start timed exercise** button. Timeout auto-submits via same form as **Submit for grading**. Timer state is session-scoped (resets on navigation away).
- **Elapsed time:** Optional form field `elapsed_seconds` on submit when learner started the timer; server validates `0 < elapsed <= duration` before recording.
- **Non-goals:** Accounts, server DB for progress, AI grading, cross-device sync, interview session queues, leaderboards, grading rule changes.

## Milestones

### 1. `TIM-38` — Progress cookie and domain model

**Goal:** Read/write signed progress cookie and define progress domain types.

**Files to create or modify:**

- `src/app/progress/__init__.py`
- `src/app/progress/cookie.py` — `load_progress(request) -> ProgressStore`, `dump_progress(store) -> str`, `attach_progress_cookie(response, store)`, constants (`COOKIE_NAME`, `MAX_AGE`, schema version).
- `src/app/domain/progress.py` — replace demo types with `ExerciseProgressStatus`, `ExerciseProgress`, `ProgressStore`, `ProgressSummary`; helpers `get_status(exercise_id)`, `passed_count()`, `apply_submit_outcome(...)`.
- `tests/test_progress_cookie.py` — sign/roundtrip, tampered cookie → empty, schema version handling, payload size sanity (50 exercises).

**Implementation notes:**

- Reuse `SESSION_SECRET` from env (same as `main._session_secret()`).
- Invalid/tampered cookies → empty `ProgressStore` (no 500).
- `apply_submit_outcome` encodes pass sticky, attempted on fail, best-time update rules from PRD edge cases.

**Acceptance criteria covered:** R1 (cookie mechanics, signing, schema, size), partial R2 (domain statuses).

**Checks:** `uv run pytest tests/test_progress_cookie.py`, ruff, mypy.

**Risks:** Cookie size if fields grow — keep per-exercise record minimal.

---

### 2. `TIM-39` — Submit wiring and clear progress

**Goal:** Update progress cookie on grade submit; add clear-progress endpoint.

**Files to create or modify:**

- `src/app/practice_session.py` — return grading result from `store_submit_result` (already does); add hook or call progress update from route layer.
- `src/app/main.py` — after `store_submit_result`, call `ProgressStore.apply_submit_outcome`; attach cookie to `RedirectResponse`. Add `POST /practice/progress/clear` → empty store + redirect to `/practice`.
- `tests/test_progress_submit.py` — TestClient with cookies: pass → `passed` persists on next GET; fail → `attempted`; fail when already `passed` unchanged; run-only does not write progress cookie.

**Implementation notes:**

- Helper `def _redirect_exercise(...) -> RedirectResponse` centralizes cookie attachment.
- Optional form field `elapsed_seconds: int | None = Form(default=None)` on submit route (wired fully in TIM-41; accept and ignore invalid values in TIM-39 if needed).
- Clear progress: POST only (form on practice page), CSRF not required for MVP (same as run/submit).

**Acceptance criteria covered:** R1 (clear control), R2 (server-side updates, run-only no-op, pass sticky).

**Checks:** `uv run pytest tests/test_progress_submit.py`, ruff, mypy.

**Risks:** Forgetting `Set-Cookie` on redirect — tests must assert cookie header on submit.

---

### 3. `TIM-40` — Catalog, home UI, and continue navigation

**Goal:** Show progress badges, aggregate counts, and continue link.

**Files to create or modify:**

- `src/app/practice.py` — accept `Request` in `get_practice_context`; load `ProgressStore`; add `progress_status` per exercise summary; `find_continue_exercise(store, difficulty_filter)`; build `ProgressSummary` for template.
- `src/app/main.py` — pass `request` into practice/index context; home gets progress summary + continue URL.
- `templates/practice.html` — progress badges on cards, passed X/50 summary, continue link (difficulty-aware when filter set), clear-progress form, updated notice copy (browser-local, 60 days).
- `templates/practice_exercise.html` — progress badge for current exercise; best elapsed display when passed timed.
- `templates/index.html` — progress summary, continue link, update deferred placeholders (remove progress/timed deferred cards).
- `src/app/main.py` — narrow `PLACEHOLDERS` list (accounts, AI, standalone catalog remain).
- `static/css/` or existing styles — badge styles if needed (minimal).
- `tests/test_app.py` — badges render, continue URL with/without difficulty filter, clear progress resets badges.

**Implementation notes:**

- Continue URL: `/practice/{dataset_id}/{exercise_id}` for next unpassed; if none, link to `/practice` with completion message.
- Home continue: no difficulty filter → full catalog order.
- Replace `DEMO_PROGRESS` usage in practice context.

**Acceptance criteria covered:** R3 (all), partial R6 (home copy).

**Checks:** `uv run pytest tests/test_app.py`, ruff, mypy.

**Risks:** `get_practice_context` signature change — update all call sites.

---

### 4. `TIM-41` — Timed exercise countdown and elapsed time

**Goal:** Timer UI, timeout submit, best elapsed time on pass.

**Files to create or modify:**

- `static/js/practice-timer.js` — countdown, start button, mm:ss display, timeout form submit, `submitting` guard, pass `elapsed_seconds` hidden input on submit.
- `templates/practice_exercise.html` — timer block for timed exercises; `data-timer-seconds`, script tag; hidden `elapsed_seconds` input.
- `src/app/main.py` — validate `elapsed_seconds` on submit when exercise is timed and timer field present.
- `src/app/domain/exercises.py` — update `MODE_OPTIONS` Timed description (no longer “later milestone”).
- `tests/test_progress_submit.py` or `tests/test_app.py` — timed pass stores elapsed; retry with lower time updates best; untimed ignores elapsed.

**Implementation notes:**

- Timeout uses `form.requestSubmit()` targeting submit formaction or programmatic click on submit button.
- Document in template comment: timer resets if user navigates away mid-countdown.
- Best time display: format seconds as `m:ss` in template filter or Python helper.

**Acceptance criteria covered:** R4 (all), R5 (all).

**Checks:** `uv run pytest`, manual smoke per `docs/phase-3-manual-test-plan.md` (created in TIM-42).

**Risks:** Double submit on timeout — client `submitting` flag required.

---

### 5. `TIM-42` — Docs, manual test plan, and validation

**Goal:** Document Phase 3 behavior and update validation/docs gates.

**Files to create or modify:**

- `README.md` — Phase 3 section (cookie progress, timed mode, 60-day lifetime, clear progress).
- `docs/phase-3-manual-test-plan.md` — cookie persistence, continue, timer, clear progress smoke steps.
- `docs/progress.md` _(new, optional)_ — cookie schema and privacy copy for reviewers.
- `tests/test_developer_workflow.py` — README/PRD index assertions for Phase 3 active.
- `prd/README.md` — Phase 3 active during implementation; mark complete when phase ships.

**Acceptance criteria covered:** R6 (all).

**Checks:** `./scripts/validate-env.sh`, full pytest, ruff, mypy.

**Risks:** None significant.

---

## Requirement coverage

| PRD requirement | Milestone(s) |
|-----------------|--------------|
| R1. Signed progress cookie | `TIM-38`, `TIM-39`, `TIM-40` (clear) |
| R2. Progress status model and updates | `TIM-38`, `TIM-39`, `TIM-41` |
| R3. Progress in catalog and navigation | `TIM-40` |
| R4. Timed exercise countdown | `TIM-41` |
| R5. Timeout submit and elapsed time | `TIM-39`, `TIM-41` |
| R6. Home, docs, and validation | `TIM-40`, `TIM-42` |

## Out of scope (explicit)

- Accounts, OAuth, server-side progress DB, AI grading, cross-device sync, multi-exercise interview sessions, leaderboards, strict grading changes, new exercises, CI Postgres.

## Engineering principles check

| Principle | Assessment |
|-----------|------------|
| Minimal scope per PR | Five milestones; one Linear issue each. |
| Design fit | Progress module beside `practice_session`; cookie helper separate from session middleware. |
| Simplicity | Server-rendered forms + small JS timer; no new dependencies. |
| DRY | Single `ProgressStore.apply_submit_outcome`; reuse submit route for timeout. |
| Tests | Unit tests for cookie + TestClient integration for submit/clear/UI. |
| Small CLs | TIM-40 is the largest (templates); still one concern (progress UI). |

**Non-blocking trade-offs:**

- Timer is client-side only — server trusts `elapsed_seconds` within bounds (acceptable for practice MVP).
- Continue ignores dataset/mode filters — matches PRD (difficulty only).

## Approval

Pending user approval of this plan. After approval:

1. Update `prd/README.md` to name Phase 3 as the active phase.
2. Create Linear epic `TIM-37` and child issues `TIM-38`–`TIM-42`.
3. Implement one issue at a time via `sql-gym-implement-issue` (or authorized `sql-gym-run-phase`).
