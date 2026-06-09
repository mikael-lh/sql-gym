# Phase 4 interview sessions and reliability polish PRD

## Status

**Complete** (shipped 2026-06-09 via epic [TIM-43](https://linear.app/times-api/issue/TIM-43/phase-4-or-interview-sessions-and-reliability-polish), PRs [#83](https://github.com/mikael-lh/sql-gym/pull/83)–[#89](https://github.com/mikael-lh/sql-gym/pull/89)). Scope: **B + D** — multi-exercise interview sessions (timed and untimed) plus catalog/reliability polish.

## Source context

This phase follows the SQL Gym product vision in `prd/00-product-vision.md`, especially interview-style drills and a trustworthy grading/feedback loop (core loop steps 3–7).

Phase 3 in `prd/phase-3-progress-and-timed-mode.md` delivered signed cookie progress (`sql_gym_progress`), catalog/home badges, continue navigation, and **per-exercise** timed mode with countdown and timeout submit. It explicitly deferred **multi-exercise interview session queues**.

Current implementation context:

- `src/app/practice_session.py` — session payload `practice_attempts` stores draft SQL, **full serialized query results** (up to 500 rows), execution errors, and grading per exercise.
- `src/app/progress/` — signed progress cookie; submit updates pass/attempt/best elapsed time.
- `static/js/practice-timer.js` — per-exercise timer with explicit start and timeout auto-submit.
- `src/app/progress/navigation.py` — `find_continue_exercise` in stable catalog order (optional difficulty filter).
- `src/app/catalog/data/times_exercises.json` — 50 exercises; 16 `Timed`; known prompt/sample SQL drift vs `reference_sql` on date-filter exercises (e.g. `times-archive-011`, `times-archive-014`).
- `templates/index.html` / `main.py` `PLACEHOLDERS` — still defer AI grading and accounts; interview **sessions** not yet offered.

**Known reliability issue (Phase 3):** storing full query grids in the session cookie can exceed browser cookie size limits (~4KB). Large passes may update the progress cookie correctly while **grading feedback fails to render** after submit because the session cookie is dropped. This was observed on exercises returning wide result sets (e.g. 500-row outputs).

## Resolved product decisions (planning, 2026-06-09)

- **Phase 4 theme:** Ship **interview sessions (B)** and **reliability/catalog polish (D)** together; defer AI grading and accounts.
- **Identity:** Still no user accounts or server-side learner database.
- **Interview sessions:** A **browser-session-scoped** queue of catalog exercises — **both timed and untimed** (not a new durable cookie). Per-exercise progress cookie updates remain unchanged on each submit.
- **Queue length:** Learner chooses **3, 5, 8**, or **Unlimited** when starting a session. Fixed lengths cap the queue; **Unlimited** runs through **all eligible exercises** in catalog order within the active filter (50 today when unfiltered). Learner may **end session early** to view summary before the queue is exhausted.
- **Resume UX:** If a session is in progress, `/practice` and home show a **Resume interview** banner/link to the current question.
- **URL shape (Option A):** Dedicated interview routes under `/practice/interview/...` (e.g. `/practice/interview/start`, `/practice/interview/{dataset_id}/{exercise_id}`, `/practice/interview/summary`). These are **one dynamic route per pattern** (same as casual practice today) — not a separate static page per exercise. Casual single-exercise URLs under `/practice/{dataset_id}/{exercise_id}` remain unchanged.
- **Exercise selection:** Sequential exercises in stable catalog order, optionally filtered by **difficulty** (same semantics as continue). **Both `Timed` and `Untimed` modes** are eligible. Queue starts from the first exercise in scope (catalog order within filter).
- **Timer behavior:** Reuse Phase 3 per-exercise timer **only when `exercise.mode == "Timed"`** (explicit start, `estimated_time_minutes`, timeout submit). Untimed queue items have no timer UI. No whole-session master clock in Phase 4.
- **Advance rules:** After submit or timeout on an interview exercise, show grading feedback, then learner clicks **Next question** (no forced auto-skip timer). Last exercise shows **View session summary** instead.
- **Session outcomes:** Session summary shows pass/fail per queued exercise, total elapsed time (sum of per-exercise elapsed when recorded), and links back to catalog. Session does not write a separate durable store; abandoning the tab ends the session.
- **Single-exercise practice:** Existing `/practice/...` timed and untimed flows remain; interview mode is an additional entry path.
- **Session payload slimming:** Session stores **grading outcomes**, SQL text, and a **bounded preview** of run results (not full 500-row grids). Display and grading after submit must remain correct.
- **Catalog polish:** Align learner-facing **prompt** and **sample_sql** text with `reference_sql` intent on audited exercises (date literals, filters). Do not change expected grids or grading rules.

## Problem

**Interview gap:** Practice works one exercise at a time. Interview prep usually means a **sequence** of questions with continuity and a recap — learners must manually pick the next card.

**Reliability gap:** Session cookies that embed full result grids are fragile. Learners can pass (progress cookie updates) but see no grading panel, which undermines trust in the product.

**Content gap:** Some exercise prompts and sample SQL still reference dates or filters that do not match the imported archive slice (`reference_sql` uses historical dates like 1920 where prompts still say 2024).

## Goals

- Offer an **interview session** flow: pick queue length (3, 5, 8, or unlimited) and optional difficulty, work through exercises (timed and untimed) in order, and view a **session summary** (on completion or early end).
- Keep strict grid-match grading and cookie progress behavior from Phases 2–3.
- Fix session storage so submit feedback is reliable even for wide result sets.
- Correct audited catalog copy so prompts and samples do not mislead learners relative to gradable SQL.
- Update home/practice copy and docs to describe interview sessions honestly.
- Keep changes testable in small PRs with documented session and session-payload rules.

## Non-goals

- User authentication, accounts, OAuth, or cross-device sync.
- AI grading, explanations, or partial credit.
- Whole-session countdown (single clock across all exercises).
- Randomized or adaptive exercise selection algorithms.
- Leaderboards, rankings, or sharing session scores.
- New datasets, new exercises beyond copy fixes, or grading rule changes.
- Durable interview history across browser restarts (sessions are session-scoped).
- CI Postgres or automated Times refresh (unless pulled in incidentally for tests).
- Standalone catalog route.

## Users and use cases

### Learner

As a learner preparing for interviews, I want to run **several SQL questions in a row** so practice feels like a real interview loop.

As a learner, I want a **summary** after the session showing which questions I passed and how long they took.

As a learner, I want grading feedback to **always appear** after submit, even when my query returns many rows.

As a learner, I want exercise **prompts and samples** to match the data I can actually query.

### Reviewer

As a reviewer, I want interview session rules and session payload limits documented so I can reproduce flows locally.

As a reviewer, I want automated tests for session queue building, advance logic, and slim session storage on large results.

### Future implementer

As a future implementer, I want interview session state isolated from progress cookie schema so accounts or server-side history can be added later.

## Requirements

### R1. Interview session entry and configuration

The app must let learners start a multi-exercise interview session from the practice surface.

Acceptance criteria:

- `/practice` (and/or home) exposes **Start interview session** (or equivalent) linking to a configuration step.
- Configuration UI lets the learner pick queue length: **3, 5, 8**, or **Unlimited** (all eligible exercises in scope).
- Optional **difficulty** filter (`Beginner`, `Intermediate`, `Advanced`) applies to which exercises are eligible, matching Phase 3 continue filter semantics.
- Copy states the session includes **timed and untimed** catalog exercises, runs in **catalog order** within the filter, and ends when the queue is complete, the learner **ends session early**, or they leave and abandon.
- Starting a session creates session state server-side in the **browser session** (not the progress cookie) and redirects to the first queued exercise.

### R2. Interview session queue and navigation

The server must build and advance a deterministic queue of catalog exercises.

Acceptance criteria:

- Queue contains exercises from `TIMES_ARCHIVE_CATALOG` in stable tuple order — **both `Timed` and `Untimed`**.
- When difficulty filter is set, queue draws only from that difficulty; when unset, all catalog exercises are eligible.
- Fixed queue lengths use `min(selected, eligible count)`; **Unlimited** queues every eligible exercise in order.
- Session state tracks: `queue` (exercise ids in order), `current_index`, `started_at`, `queue_mode` (`fixed` | `unlimited`), and per-exercise outcomes (`passed`/`failed`, `elapsed_seconds` when available).
- Exercise preview in interview context shows **Question X of Y** (fixed) or **Question X** with optional “of N exercises” hint (unlimited); interview-mode chrome distinct from casual practice.
- **End session early** ends the interview and opens the summary for exercises completed so far (available for any queue mode).
- `/practice` and home show **Resume interview** when session state exists and the queue is not finished.
- Interview exercises are served at `/practice/interview/{dataset_id}/{exercise_id}`; configuration at `/practice/interview/start`; summary at `/practice/interview/summary`. No standalone catalog route.
- Leaving mid-session (navigate to catalog/home) preserves session state until the browser session ends; learner can resume current question if session state exists.
- **Abandon session** control clears interview session state and returns to `/practice`.

### R3. Per-exercise mode and advance within session

Interview exercises reuse Phase 3 per-exercise behavior with session-aware navigation.

Acceptance criteria:

- Queued exercises with `mode == "Timed"` show the existing timer UI (explicit start, countdown, timeout submit). **Untimed** queue items omit the timer panel.
- On manual submit or timeout, grading uses the existing submit path; progress cookie updates per Phase 3 rules.
- After grading renders, UI shows **Next question**, **End session early**, or **View session summary** on the last queued exercise; no auto-advance without learner action.
- Timeout on a failed/empty query records `failed` for session summary; progress cookie follows Phase 3 attempted rules.
- `elapsed_seconds` for timed passes is recorded in both progress cookie (best time) and session outcome.
- Client prevents double submit on timeout (existing `submitting` guard retained).

### R4. Session summary

After the last exercise—or **End session early**—learners see a recap of the interview session.

Acceptance criteria:

- Summary page lists each queued exercise with title, pass/fail, and elapsed time when recorded.
- Shows aggregate stats: **passed count / queue length** and **total elapsed time** (sum of per-exercise elapsed values present).
- Links: **Practice catalog**, **Start new session**, and per-exercise links for review.
- Completing or abandoning a session clears interview session state appropriately (complete after summary viewed or explicit abandon).
- Session summary does not persist across browser restarts.

### R5. Session payload slimming (reliability)

Session attempt storage must not embed unbounded query grids.

Acceptance criteria:

- `practice_attempts` session entries store at most **25 preview rows** for run/submit display (configurable constant in code), plus `columns`, `row_count`, and `truncated` flag.
- Grading after submit still works for full-width results (server re-executes SQL on submit; no dependency on full grid in session).
- After submit on exercises with large results, **grading panel renders** (`#grading-title` / feedback visible) in integration tests.
- Regression test reproduces the Phase 3 failure mode (wide result) and asserts grading UI present.
- Document session vs progress split in `docs/progress.md` or new `docs/session-state.md`.

### R6. Catalog content alignment

Learner-facing exercise copy must match gradable intent.

Acceptance criteria:

- Audit all 50 exercises for learner-facing copy drift across four fields in `times_exercises.json`:
  - **`prompt`** — natural-language task text shown as the exercise headline.
  - **`hint`** — short nudge (must not contradict gradable SQL).
  - **`sample_sql`** — illustrative SQL in `<details>` (learners often copy-paste).
  - **`reference_sql`** — canonical answer used to build expected grids (not shown to learners; audit baseline).
- Fix mismatches where prompt/sample/hint would lead learners to SQL that **cannot pass** strict grading, without changing expected grids or `reference_sql` unless a grid bug is found (grid bugs out of scope unless blocking).
- Minimum fixes include **`times-archive-011`** and **`times-archive-014`** (date literal drift; see examples in PR discussion).
- No separate content-audit doc required; summarize catalog copy fixes in the implementation PR description only.
- Optional scripted guard: flag exercises whose prompt mentions a calendar year that does not appear in `reference_sql` (implementation plan may scope).

### R7. Home, docs, and validation

Copy and docs reflect Phase 4 boundaries honestly.

Acceptance criteria:

- Home and/or practice describe **interview sessions** and link to the new flow.
- Remove or narrow any placeholder that implied interview queues are deferred.
- README Phase 4 section documents interview sessions and session reliability change.
- `./scripts/validate-env.sh` remains the validation entry point; new tests under `uv run pytest`.
- `docs/phase-4-manual-test-plan.md` covers interview flow, summary, abandon, and large-result submit feedback.

## Edge cases and error states

| Case | Expected behavior |
|------|-------------------|
| Fewer exercises than requested fixed queue length | Use all eligible exercises; show actual count in UI before start |
| Unlimited with difficulty filter | Queue includes all exercises in that difficulty only |
| End session early with zero completes | Summary shows empty state with link back to catalog |
| No exercises for difficulty filter | Configuration shows zero available; start disabled with explanation |
| Untimed question in interview queue | No timer UI; manual submit only; no `elapsed_seconds` in session outcome |
| Session cookie lost mid-interview | Session queue lost; progress cookie retains any passes already written |
| Large query result on run | Preview capped; row count and truncated flag shown |
| Large query result on submit | Grading renders; session stores grading + slim preview only |
| Learner opens same exercise outside interview while session active | Acceptable; session state and single-exercise practice coexist; document as unsupported edge case |
| Timer expires with empty SQL | Failed outcome in session; attempted in progress cookie per Phase 3 |
| All queue exercises already `passed` in progress cookie | Session still runnable; summary shows pass/fail for this session attempt |
| Double submit / timeout race | Client `submitting` guard prevents duplicate posts |

## Success signals

Phase 4 is successful when a reviewer can:

1. Start a 3-question interview on **Beginner** exercises (mix of timed and untimed) and advance through the queue to a summary.
2. See grading feedback after submitting a query that returns hundreds of rows.
3. Confirm progress cookie still updates on interview submits.
4. Read corrected date copy on `times-archive-011` and `times-archive-014`.
5. Run `./scripts/validate-env.sh` and documented manual steps successfully.

## Relationship to Phase 3

| Phase 3 behavior | Phase 4 change |
|------------------|----------------|
| Per-exercise timed mode | Unchanged for casual `/practice/{id}`; timer shown in interview only for `Timed` queue items |
| Progress cookie | Unchanged; still updated on each submit |
| Continue link | Unchanged; interview is a separate entry path |
| Full grids in session | Replaced with capped preview + metadata |
| Interview queues deferred | Implemented as session-scoped queue |

## What was actually built

- `app/interview/` — queue builder, session domain, view helpers.
- Interview routes: start, exercise run/submit, next, end, abandon, summary.
- Session preview cap (`SESSION_PREVIEW_ROW_LIMIT = 25`) in `practice_session.py`.
- Catalog copy fixes for `times-archive-011` and `times-archive-014` (1920 dates).
- Docs: [session-state.md](../docs/session-state.md), [phase-4-manual-test-plan.md](../docs/phase-4-manual-test-plan.md).

## Approved deviations

| Topic | PRD / plan | Shipped |
|-------|------------|---------|
| Truncated result copy | Distinct execution vs session preview messaging | Reuses existing “500 rows” template when session-capped; acceptable for MVP |
| Content audit log | No separate audit doc | Summarized in PR #88 description only |
| Optional year guard script | Deferred unless trivial | Deferred; spot tests in `test_catalog_content.py` |

### Linear issue ID mapping

| Order | Plan milestone | Linear issue | PR |
|------:|----------------|--------------|-----|
| 1 | TIM-44 | **TIM-44** | [#83](https://github.com/mikael-lh/sql-gym/pull/83) |
| 2 | TIM-45 | **TIM-49** | [#84](https://github.com/mikael-lh/sql-gym/pull/84) |
| 3 | TIM-46 | **TIM-50** | [#85](https://github.com/mikael-lh/sql-gym/pull/85) |
| 4 | TIM-47 | **TIM-46** | [#86](https://github.com/mikael-lh/sql-gym/pull/86) |
| 5 | TIM-48 | **TIM-47** | [#87](https://github.com/mikael-lh/sql-gym/pull/87) |
| 6 | TIM-49 | **TIM-48** | [#88](https://github.com/mikael-lh/sql-gym/pull/88) |
| 7 | TIM-50 | **TIM-45** | [#89](https://github.com/mikael-lh/sql-gym/pull/89) |

Full detail: [`docs/phase-4-implementation-plan.md`](../docs/phase-4-implementation-plan.md#linear-issue-mapping).

## Future work

- Accounts and cross-device sync.
- AI grading and explanations.
- Whole-session master clock; randomized or adaptive queues.
- Scripted catalog year guard (`scripts/check_catalog_copy.py`).
- Distinct template copy for session preview vs execution truncation.

## Open questions

- None blocking post-ship.
