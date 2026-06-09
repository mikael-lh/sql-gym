# Phase 4 implementation plan

## Status

**Complete** — implemented via [TIM-43](https://linear.app/times-api/issue/TIM-43/phase-4-or-interview-sessions-and-reliability-polish) epic (PRs [#83](https://github.com/mikael-lh/sql-gym/pull/83)–[#89](https://github.com/mikael-lh/sql-gym/pull/89)).

## Source

- PRD: `prd/phase-4-interview-sessions-and-polish.md` (approved via [#81](https://github.com/mikael-lh/sql-gym/pull/81))
- Proposed Linear epic: **TIM-43** _(create after plan approval)_
- Proposed child issues: **TIM-44** → **TIM-50** (implementation order below)

## Planning decisions

- **Interview session store:** Starlette session key `interview_session` (separate from `practice_attempts`). Browser-session scoped; not written to progress cookie.
- **Session payload shape (v1):**
  ```json
  {
    "v": 1,
    "queue": ["times-archive-005", "..."],
    "current_index": 0,
    "queue_mode": "fixed",
    "requested_length": 5,
    "difficulty": "Beginner",
    "started_at": "<iso-utc>",
    "outcomes": {
      "times-archive-005": { "passed": true, "elapsed_seconds": 420 }
    },
    "status": "active"
  }
  ```
  `requested_length` is `null` when `queue_mode` is `unlimited`. `status` is `active` | `ended_early` | `completed`.
- **Queue builder:** `build_interview_queue(requested_length: int | None, difficulty: Difficulty | None) -> list[Exercise]` — **all catalog exercises** (timed and untimed), stable catalog order, optional difficulty filter. Fixed lengths use `min(requested, eligible)`; unlimited returns all eligible exercises (50 unfiltered today).
- **Routes (Option A):** One **parameterized handler** per pattern — not a separate route file or template per exercise. `{dataset_id}` and `{exercise_id}` are path variables; the server loads that exercise from the catalog (same model as existing `/practice/{dataset_id}/{exercise_id}`).
  - `GET /practice/interview/start` — configuration form
  - `POST /practice/interview/start` — create session → redirect to first question
  - `GET /practice/interview/{dataset_id}/{exercise_id}` — interview exercise page
  - `POST /practice/interview/{dataset_id}/{exercise_id}/run` — run SQL (redirect back)
  - `POST /practice/interview/{dataset_id}/{exercise_id}/submit` — grade + progress cookie + record outcome → redirect back
  - `POST /practice/interview/next` — advance `current_index` → redirect to next question URL
  - `POST /practice/interview/end` — end early → summary
  - `POST /practice/interview/abandon` — clear session → `/practice`
  - `GET /practice/interview/summary` — recap; clears session after render
- **Guards:** Interview exercise GET/POST handlers verify `exercise_id` matches `queue[current_index]`; otherwise redirect to current question or `/practice/interview/start` if session missing.
- **Timer:** Reuse `practice-timer.js` and timed exercise template block **only when `exercise.mode == "Timed"`**. Untimed interview questions omit the timer panel.
- **Session slimming:** `SESSION_PREVIEW_ROW_LIMIT = 25` in `practice_session.py`; serialize at most 25 rows per stored `query_result`. Grading on submit still re-executes SQL server-side.
- **Catalog audit:** Agent manually audits all 50 exercises; fixes in `times_exercises.json`; summarize changes in PR description only (no `docs/phase-4-content-audit.md`).
- **Optional year guard:** Defer scripted `scripts/check_catalog_copy.py` unless trivial; not blocking Phase 4.
- **Non-goals:** Accounts, AI grading, whole-session master clock, randomized queues, durable interview history, CI Postgres.

## Milestones

### 1. TIM-44 — Session payload slimming

**Goal:** Cap run/submit result rows stored in session so grading UI survives large queries.

**Files to create or modify:**

- `src/app/practice_session.py` — `SESSION_PREVIEW_ROW_LIMIT = 25`; slice rows in `_serialize_query_result`; preserve `row_count` and `truncated`.
- `tests/test_practice_session.py` _(new)_ — unit tests for preview cap and metadata preservation.
- `tests/test_app.py` or `tests/test_progress_submit.py` — regression: submit wide result (exercise with 500-row expected grid, mocked or live DB) asserts `#grading-title` in response HTML.

**Implementation notes:**

- Template `practice_exercise.html` already shows truncated copy when `query_result.truncated`; preview may show fewer than 25 rows while `row_count` reflects full execution.
- Do not change execution `MAX_ROWS` (500) or grading logic.

**Acceptance criteria covered:** R5 (all).

**Checks:** `uv run pytest tests/test_practice_session.py` + regression test, ruff, mypy.

**Risks:** Low; verify templates handle `row_count > len(rows)` display honestly.

---

### 2. TIM-45 — Interview session domain and queue builder

**Goal:** Define interview session types, queue construction, and session read/write helpers.

**Files to create or modify:**

- `src/app/interview/__init__.py`
- `src/app/interview/session.py` — `InterviewSession`, `InterviewOutcome`, `load_interview_session`, `save_interview_session`, `clear_interview_session`, `record_outcome`, `current_exercise`, `advance`, `build_summary`.
- `src/app/interview/queue.py` — `build_interview_queue`, `count_eligible_exercises`, `QueueLength` enum or constants (`3`, `5`, `8`, `unlimited`).
- `tests/test_interview_queue.py` — fixed/unlimited lengths, difficulty filter, timed+untimed inclusion, stable order, min when fewer than requested.
- `tests/test_interview_session.py` — roundtrip session state, outcome recording, advance index.

**Implementation notes:**

- Reuse `Difficulty` from `app.domain.exercises`.
- `eligible_interview_exercises(difficulty)` iterates `TIMES_ARCHIVE_CATALOG.exercises` like `find_continue_exercise` (no mode filter).

**Acceptance criteria covered:** Partial R2 (queue rules, session state model).

**Checks:** `uv run pytest tests/test_interview_*.py`, ruff, mypy.

**Risks:** Keep session JSON compact (outcomes map only; no SQL duplication in interview session).

---

### 3. TIM-46 — Interview start and session creation

**Goal:** Configuration UI and POST handler to start an interview.

**Files to create or modify:**

- `src/app/interview/views.py` — `get_interview_start_context(request)`.
- `src/app/main.py` — `GET/POST /practice/interview/start`.
- `templates/interview_start.html` — length radio (3/5/8/Unlimited), difficulty select (optional), eligible count preview, disabled start when zero exercises match filter.
- `tests/test_interview_routes.py` _(new)_ — start page renders; POST creates session and redirects to first queued exercise URL.

**Implementation notes:**

- POST validates length and difficulty; builds queue; sets `current_index=0`, `status=active`.
- Redirect target: `/practice/interview/{dataset_id}/{exercise_id}`.

**Acceptance criteria covered:** R1 (all), partial R2 (session creation).

**Checks:** `uv run pytest tests/test_interview_routes.py`, ruff, mypy.

**Risks:** Route ordering in `main.py` — register `/practice/interview/start` before parameterized `{dataset_id}` routes.

---

### 4. TIM-47 — Interview exercise page, run/submit, and advance

**Goal:** Interview exercise experience with per-exercise timer (when timed), grading, and manual advance.

**Files to create or modify:**

- `src/app/interview/views.py` — `get_interview_exercise_context(request, dataset_id, exercise_id)`; navigation helpers (`next_url`, `is_last_question`, question labels).
- `src/app/main.py` — interview GET exercise, POST run, POST submit, POST next, POST end.
- `templates/interview_exercise.html` — based on `practice_exercise.html` with interview chrome (`Question X of Y`), timer block conditional on `Timed`, formactions under `/practice/interview/...`, post-grade actions: **Next question**, **End session early**, **View session summary** (last item).
- `static/styles.css` — minimal interview badge/panel styles if needed.
- `tests/test_interview_routes.py` — run/submit on interview path updates progress cookie + session outcome; next advances; wrong exercise id redirects to current.

**Implementation notes:**

- Submit handler: reuse `store_submit_result`, `load_progress` / `apply_submit_outcome`, `record_outcome` on interview session; redirect to same interview exercise URL (grading visible).
- `POST /practice/interview/next` increments index after outcome exists for current exercise; redirect to next interview URL.
- `POST /practice/interview/end` sets `status=ended_early`, redirect to summary.
- Interview submit must use interview redirect paths (not casual `/practice/...`).
- Extract shared grading/progress submit helper in `main.py` if duplication grows (small private function acceptable).

**Acceptance criteria covered:** R2 (exercise routes, guards, end early), R3 (all).

**Checks:** `uv run pytest tests/test_interview_routes.py`, ruff, mypy.

**Risks:** Largest milestone; keep template diff focused. Timer JS unchanged if form structure matches practice page.

---

### 5. TIM-48 — Summary, abandon, and resume banner

**Goal:** Session recap and discoverability from home/practice.

**Files to create or modify:**

- `src/app/interview/views.py` — `get_interview_summary_context`.
- `src/app/main.py` — `GET /practice/interview/summary`, `POST /practice/interview/abandon`.
- `templates/interview_summary.html` — outcomes table, passed/total, total elapsed, empty state, links.
- `src/app/practice.py` — `interview_resume_context(request)` for home/practice templates.
- `templates/index.html`, `templates/practice.html` — **Resume interview** banner when active session.
- `templates/practice.html`, `templates/index.html` — **Start interview session** link.
- `tests/test_interview_routes.py` — summary after complete/end early; abandon clears session; resume link present when active.

**Implementation notes:**

- Summary GET clears `interview_session` after render (or on load with `status=completed`).
- Total elapsed = sum of `outcomes[*].elapsed_seconds` where present.

**Acceptance criteria covered:** R4 (all), R2 (resume, abandon), partial R1 (entry links).

**Checks:** `uv run pytest`, ruff, mypy.

**Risks:** Ensure resume URL points to `queue[current_index]` even if user partially advanced.

---

### 6. TIM-49 — Catalog content alignment

**Goal:** Fix learner-facing copy that blocks strict grading.

**Files to create or modify:**

- `src/app/catalog/data/times_exercises.json` — audit all 50; fix `prompt`, `hint`, `sample_sql` where they mislead vs `reference_sql` (minimum `times-archive-011`, `times-archive-014`).
- `tests/test_catalog_content.py` _(optional, small)_ — assert 011/014 prompts reference 1920 dates; or spot-check via parameterized strings.

**Implementation notes:**

- Do not change `reference_sql` or expected grid files unless a blocking bug is found.
- Summarize all copy edits in PR description only.

**Acceptance criteria covered:** R6 (all).

**Checks:** `uv run pytest`, ruff; PR description lists exercises touched.

**Risks:** Low; keep diffs copy-only.

---

### 7. TIM-50 — Docs, manual test plan, and validation

**Goal:** Document Phase 4 and update repo gates.

**Files to create or modify:**

- `README.md` — Phase 4 section (interview sessions, session slimming).
- `docs/session-state.md` _(new)_ — session vs progress cookie, interview session shape, preview row cap.
- `docs/progress.md` — cross-link session-state doc.
- `docs/phase-4-manual-test-plan.md` — interview start, 3-question flow (timed + untimed), unlimited, end early, abandon, resume, large-result grading, catalog spot-check.
- `tests/test_developer_workflow.py` — README Phase 4 assertions.
- `scripts/validate-env.sh` — active phase banner when implementation completes.
- `src/app/main.py` — update `PLACEHOLDERS` / home `status_label` if needed.
- `prd/README.md` — mark Phase 4 active during implementation; complete after ship.

**Acceptance criteria covered:** R7 (all).

**Checks:** `./scripts/validate-env.sh`, full pytest, ruff, mypy.

**Risks:** None significant.

---

## Requirement coverage

| PRD requirement | Milestone(s) |
|-----------------|--------------|
| R1. Interview entry and configuration | TIM-46, TIM-48 |
| R2. Queue and navigation | TIM-45, TIM-46, TIM-47, TIM-48 |
| R3. Timer and advance within session | TIM-47 |
| R4. Session summary | TIM-48 |
| R5. Session payload slimming | TIM-44 |
| R6. Catalog content alignment | TIM-49 |
| R7. Home, docs, validation | TIM-50 |

## Out of scope (explicit)

- Accounts, OAuth, server-side learner DB, AI grading, cross-device sync.
- Whole-session master clock, randomized queues, leaderboards.
- `docs/phase-4-content-audit.md` or separate audit log file.
- CI Postgres, new datasets, grading rule changes, standalone catalog route.

## Engineering principles check

| Principle | Assessment |
|-----------|------------|
| Minimal scope per PR | Seven milestones; one Linear issue each. |
| Design fit | `app/interview/` beside `app/progress/`; session slimming in `practice_session`. |
| Simplicity | Server-rendered forms; reuse timer JS and grading paths. |
| DRY | Shared submit grading helper between practice and interview POST handlers. |
| Tests | Unit tests for queue/session; route tests for interview flow; regression for slim session. |
| Small CLs | TIM-47 is largest (templates + routes); still one concern. |

**Non-blocking trade-offs:**

- Interview session and casual practice on the same exercise in parallel tabs — documented unsupported edge case.
- Summary clears session on view; no “review summary again” without re-running (acceptable for session-scoped MVP).
- Optional catalog year script deferred.

## Linear issue mapping

Plan milestone labels **TIM-44**–**TIM-50** differ from Linear child issue IDs (same pattern as Phase 3). Use **Linear ID** when linking issues or PRs.

| Order | Plan milestone | Linear issue | PR |
|------:|----------------|--------------|-----|
| 1 | TIM-44 (session slimming) | **TIM-44** | [#83](https://github.com/mikael-lh/sql-gym/pull/83) |
| 2 | TIM-45 (interview domain) | **TIM-49** | [#84](https://github.com/mikael-lh/sql-gym/pull/84) |
| 3 | TIM-46 (start flow) | **TIM-50** | [#85](https://github.com/mikael-lh/sql-gym/pull/85) |
| 4 | TIM-47 (exercise routes) | **TIM-46** | [#86](https://github.com/mikael-lh/sql-gym/pull/86) |
| 5 | TIM-48 (summary/resume) | **TIM-47** | [#87](https://github.com/mikael-lh/sql-gym/pull/87) |
| 6 | TIM-49 (catalog audit) | **TIM-48** | [#88](https://github.com/mikael-lh/sql-gym/pull/88) |
| 7 | TIM-50 (docs) | **TIM-45** | [#89](https://github.com/mikael-lh/sql-gym/pull/89) |

## Approval

Plan approved and implemented 2026-06-09.
