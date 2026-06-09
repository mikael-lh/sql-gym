# Phase 3 progress and timed mode PRD

## Status

**Complete** (merged 2026-06-09). Implemented via [TIM-37](https://linear.app/times-api/issue/TIM-37/phase-3-or-progress-and-timed-mode) child issues TIM-42, TIM-41, TIM-38, TIM-39, and TIM-40 and [`docs/phase-3-implementation-plan.md`](../docs/phase-3-implementation-plan.md).

## Source context

This phase follows the SQL Gym product vision in `prd/00-product-vision.md`, especially core loop steps 3, 6, and 7: choose timed or untimed practice, see an attempt result, and move to the next exercise.

Phase 2 in `prd/phase-2-sql-execution-grading.md` delivered PostgreSQL execution, strict grid-match grading for all 50 Times Archive exercises, CodeMirror on exercise previews, and **session-only** attempt state via Starlette `SessionMiddleware`.

Current implementation context:

- `src/app/practice_session.py` — per-exercise attempt state in `request.session["practice_attempts"]` (SQL draft, last run result, last grading outcome).
- `src/app/domain/progress.py` — `ProgressSummary` and `DEMO_PROGRESS` placeholder only.
- `src/app/domain/attempts.py` — `AttemptStatus` (`not_started`, `draft`, `submitted`, `graded`); demo model unused on gradable paths.
- `src/app/domain/exercises.py` — `PracticeMode` (`Untimed`, `Timed`); 16 catalog exercises use `Timed`.
- `templates/practice.html` — catalog browsing; exercise cards do not show learner progress.
- `templates/practice_exercise.html` — run/submit flows; no timer UI.
- `templates/index.html` and `src/app/main.py` — home still lists durable progress and timed scoring as deferred.
- `pyproject.toml` / `SessionMiddleware` — signed session cookie (`SESSION_SECRET`); default session cookie is browser-session-only (no `max_age`).

## Resolved product decisions (planning, 2026-06-08)

- **Identity:** No user accounts, sign-in, or server-side learner database in Phase 3.
- **Progress persistence:** Signed HTTP-only cookie holding a minimal progress map (exercise id → status metadata). Separate from the existing session payload that stores draft SQL and last run results.
- **Progress truth:** An exercise is **passed** only after strict grid-match grading succeeds (unchanged Phase 2 rules). **Attempted** means at least one submit-grade without pass.
- **Timed mode scope:** Per-exercise countdown on catalog exercises with `mode: "Timed"` only (16 exercises today). No multi-exercise interview session queue in Phase 3.
- **Timer duration:** Use each exercise’s existing `estimated_time_minutes` catalog field converted to a countdown.
- **Timer start:** Learner explicitly starts the timer (not auto-start on page load) so opening a timed preview is not immediately punitive.
- **Timeout behavior:** When the countdown reaches zero, auto-submit the current editor SQL for grading (same POST path as manual submit). Empty SQL surfaces the existing empty-query validation message.
- **Timed outcome:** Pass/fail remains strict grid-match only; elapsed time is recorded for display when the learner passes a timed exercise. No separate “speed score” or partial credit.
- **Cross-device:** Progress is device/browser specific; clearing cookies resets progress. UI copy must state this honestly.
- **Cookie lifetime:** `sql_gym_progress` cookie with `max_age=5184000` (60 days). Re-set on each progress write so the expiry window refreshes from that moment.
- **Continue link:** Next unpassed exercise uses **stable catalog order**. If the learner has a **difficulty filter** active on `/practice`, continue within that difficulty only. Home continue (no filter) uses full catalog order.
- **Retries after pass:** Learners may re-run and re-submit passed exercises (including timed). `passed` stays sticky; for timed passes, **best** `elapsed_seconds` (lowest) is kept and displayed.

## Problem

Learners can run SQL and receive pass/fail grading, but progress resets when the browser session ends and the catalog gives no signal for what they have completed. Timed exercises are labeled in the catalog but behave identically to untimed ones — there is no countdown, no timeout submit, and no time-on-task feedback.

The product vision’s core loop still stops short on **step 7** (move to the next exercise with continuity) and **step 3** (timed format is metadata only).

## Goals

- Persist learner progress across browser restarts without accounts, using a frictionless signed cookie.
- Show progress on the practice catalog and exercise previews (not started / attempted / passed).
- Surface aggregate progress on home and/or practice (e.g. passed count, link to continue).
- Activate timed mode on timed catalog exercises with a clear countdown and timeout submit.
- Record elapsed time when a timed exercise is passed and show it in progress UI.
- Preserve placeholder honesty for capabilities still deferred (AI grading, accounts, cross-device sync, interview session queues).
- Keep changes testable in small PRs with documented cookie and timer behavior.

## Non-goals

- User authentication, accounts, OAuth, or email.
- Server-side progress database or admin dashboards.
- Cross-browser or cross-device progress sync.
- AI grading, explanations, or partial credit.
- Multi-exercise timed “interview sessions” or randomized exercise queues.
- Leaderboards, streaks with calendar semantics, or gamification beyond simple counts.
- Changing strict grid-match grading rules from Phase 2.
- Standalone catalog route (catalog stays in `/practice`).
- Arbitrary user-uploaded datasets or new exercise content beyond progress/timer wiring.

## Users and use cases

### Learner

As a learner, I want my passed exercises to still show as passed when I return tomorrow so I can see what I have finished without creating an account.

As a learner, I want the catalog to show which exercises I have passed or attempted so I can pick what to work on next.

As a learner, I want a “continue” path to the next exercise I have not passed so I do not have to hunt through 50 cards.

As a learner, I want timed exercises to run with a visible countdown and submit when time is up so practice feels like interview prep.

As a learner, I want to know that progress lives on this browser only and can be cleared with cookies.

### Reviewer

As a reviewer, I want progress and timer behavior documented and deterministic so I can reproduce them locally.

As a reviewer, I want tests for cookie serialization, progress merge on submit, and timed-exercise UI guards without requiring accounts.

### Future implementer

As a future implementer, I want progress stored in a small signed cookie payload so accounts or a progress API can replace it later without rewriting grading.

## Requirements

### R1. Signed progress cookie (no accounts)

The app must persist per-exercise progress in a signed, HTTP-only cookie without user accounts.

Acceptance criteria:

- Progress is stored separately from session attempt drafts (SQL text, last query result) so session cookies can remain session-scoped while progress survives browser restarts.
- Cookie payload is signed with the existing app secret (`SESSION_SECRET` or a dedicated `PROGRESS_COOKIE_SECRET` documented in `.env.example`; prefer reusing `SESSION_SECRET` unless size or rotation needs justify a split).
- Cookie name is `sql_gym_progress`, `max_age=5184000` (60 days), refreshed on each progress write.
- Cookie is `HttpOnly`, `SameSite=Lax`, and `Secure` in production-like environments when applicable.
- Cookie carries a versioned schema, e.g. `{ "v": 1, "exercises": { "<exercise_id>": { "status": "passed"|"attempted", "passed_at": "<iso>", "elapsed_seconds": <int|null> } } } }`.
- Maximum payload size stays practical for a cookie (50 exercises × minimal fields); implementation must not store full query results in the progress cookie.
- A “Clear my progress” control resets the progress cookie and confirms in UI copy that this is local to the browser.
- Docs explain that progress is anonymous, device-local, and lost if cookies are cleared.

### R2. Progress status model and updates

Progress status must reflect grading outcomes from Phase 2 submit flow.

Acceptance criteria:

- Domain model defines learner progress statuses aligned with catalog exercises: `not_started`, `attempted`, `passed`.
- On successful strict grid-match pass, progress for that exercise becomes `passed` and records `passed_at` (UTC ISO string).
- On submit-grade fail, progress becomes `attempted` unless already `passed` (pass is sticky).
- Run-only (no submit) does not change progress status.
- Progress updates occur server-side in the submit handler after grading, not only in client JS.
- Tests cover pass sticky behavior, attempted after fail, and no-op on run-only.

### R3. Progress in catalog and navigation

Learners must see progress while browsing and move to the next incomplete exercise.

Acceptance criteria:

- Exercise cards on `/practice` show a progress badge or label (`Not started`, `Attempted`, `Passed`).
- Passed exercises are visually distinct (e.g. checkmark or badge) without hiding them from the catalog.
- Exercise preview shows current progress status for that exercise.
- A **Continue practicing** link on home and/or `/practice` opens the next exercise that is not `passed`, in stable catalog order.
- On `/practice`, when a **difficulty** filter is active, continue selects the next unpassed exercise **within that difficulty only** (same catalog order, filtered). Other active filters (dataset, mode) do not narrow continue unless difficulty is set.
- On home (no filter context), continue uses the full catalog in stable order.
- When all exercises are passed, continue link copy reflects completion (e.g. “All exercises passed — browse catalog”).
- Aggregate summary shows at least **passed count / total** (50 for Times Archive) on practice and/or home.
- `DEMO_PROGRESS` placeholder is replaced with real cookie-backed metrics on pages that show progress.

### R4. Timed exercise countdown

Timed catalog exercises must enforce a per-exercise countdown.

Acceptance criteria:

- Timer UI appears only when `exercise.mode == "Timed"`.
- Timer duration equals `estimated_time_minutes × 60` seconds from catalog data.
- Learner must click an explicit control (e.g. **Start timed exercise**) to begin the countdown; timer does not start automatically on page load.
- While timer is running, UI shows remaining time (mm:ss) and timed mode label.
- No pause control in Phase 3.
- If the learner navigates away before starting the timer, no time is consumed.
- If the learner navigates away after starting, timer state may reset on return (session-scoped timer state is acceptable); document behavior.

### R5. Timeout submit and elapsed time

When time expires, the app must submit for grading and record elapsed time on pass.

Acceptance criteria:

- At countdown zero, client triggers the same submit-grade flow as the **Submit for grading** button with current editor SQL.
- Timeout submit uses the existing server grading path; no duplicate grading logic.
- If SQL is empty at timeout, learner sees the same validation/error treatment as manual submit with empty SQL.
- On pass, `elapsed_seconds` from timer start to successful submit is stored in progress metadata for that exercise.
- Timed exercise preview displays best elapsed time after a pass (e.g. “Passed in 8:42”); learners may retry timed exercises without losing `passed`, and a faster pass updates the stored best time.
- Untimed exercises do not show timer UI and do not record `elapsed_seconds`.
- Tests or documented manual plan cover timeout submit and elapsed time persistence in the progress cookie.

### R6. Home, docs, and validation

Copy and docs must reflect Phase 3 boundaries honestly.

Acceptance criteria:

- Home and practice pages remove or narrow “durable progress deferred” placeholder where progress now works; still defer accounts and cross-device sync.
- Timed-mode placeholder on home is removed or updated to describe working per-exercise timers.
- README Phase 3 section documents cookie-based progress and timed mode behavior.
- `./scripts/validate-env.sh` remains the full validation entry point; new tests run under `uv run pytest`.
- Optional: short `docs/phase-3-manual-test-plan.md` with cookie persistence and timer smoke steps.

## Edge cases and error states

| Case | Expected behavior |
|------|-------------------|
| Progress cookie missing or tampered | Treat as empty progress; do not error the page |
| Progress cookie schema version unknown | Ignore or reset with safe default; document migration approach |
| Cookie exceeds size limit | Implementer must prevent bloat (no SQL/result storage); PRD acceptance includes staying under typical 4KB budget |
| Submit pass after prior `attempted` | Upgrade to `passed`; store `elapsed_seconds` if timed |
| Submit pass after prior `passed` (retry) | Remain `passed`; update `elapsed_seconds` only if new time is lower (best time) |
| Submit fail after `passed` | Remain `passed`; best time unchanged |
| Timed exercise opened in two tabs | Undefined race; acceptable to document as “last write wins” for Phase 3 |
| Timer expires during in-flight submit | Avoid double submit; client guards with a submitting flag |
| User clears progress | All exercises return to `not_started`; session attempt drafts may remain until session ends |
| Private browsing | Progress lasts for browsing session only if browser discards persistent cookies; copy warns about private mode |

## Success signals

Phase 3 is successful when a reviewer can:

1. Pass an exercise, close the browser, reopen, and still see **Passed** on the catalog card.
2. Use **Continue practicing** to reach the next incomplete exercise without manual search.
3. Open a timed exercise, start the timer, and see auto-submit at zero with grading feedback.
4. See elapsed time on a timed pass in the exercise preview or catalog metadata.
5. Clear progress locally and confirm badges reset.
6. Run documented validation commands successfully.

## Relationship to Phase 2

| Phase 2 behavior | Phase 3 change |
|------------------|----------------|
| Session-only `practice_attempts` | Unchanged for draft SQL / last run; progress summary moves to persistent cookie |
| Strict grid-match grading | Unchanged; still sole pass criterion |
| Timed label in catalog only | Timer + timeout submit for `Timed` exercises |
| `DEMO_PROGRESS` on practice | Real cookie-backed metrics |

## Progress cookie mechanics

Phase 3 adds a **second cookie** alongside the existing Starlette **session** cookie. They serve different jobs:

| Cookie | Purpose | Lifetime (Phase 3) |
|--------|---------|-------------------|
| Session (existing) | Draft SQL, last run result, last grading on the current visit | Browser session (unchanged) |
| `sql_gym_progress` (new) | Compact map of exercise id → status / pass time / best elapsed time | 60 days, refreshed on each write |

**Read path (most requests):** On every request, the server reads `sql_gym_progress` from `request.cookies`, verifies the signature, and deserializes the payload. Catalog, home, and exercise pages use that data to render badges and counts. No `Set-Cookie` is required on read-only GET responses.

**Write path (progress changes):** When progress changes — successful pass, failed submit marking `attempted`, clear-progress action, or best-time update on timed retry — the handler updates the in-memory progress map and returns a response with a **`Set-Cookie`** header containing the new signed payload. The browser stores it and automatically sends it on all later requests to the app.

Concrete write triggers in Phase 3:

- `POST …/submit` after grading (pass → `passed`, fail → `attempted` if not already passed).
- `POST` clear-progress endpoint (or equivalent) → empty map, cookie cleared or overwritten.
- Timed pass retry with a lower `elapsed_seconds` → update best time in cookie.

**Not** written on: `POST …/run` only, ordinary page views, or failed submits when already `passed`.

Implementation note: unlike `SessionMiddleware`, which attaches the session cookie automatically, the progress cookie is set explicitly via `Response.set_cookie()` (or a small helper) in handlers that mutate progress. Signing should use the same secret material as sessions (`SESSION_SECRET`) and the same pattern as Starlette’s signed cookies (e.g. `itsdangerous`), so payloads cannot be forged client-side.

## What was actually built

- Signed `sql_gym_progress` cookie (60-day lifetime) with `ProgressStore` domain model.
- Progress updates on submit-grade; `POST /practice/progress/clear`.
- Catalog/home continue link (difficulty-aware on `/practice`); progress badges; X/50 summary.
- Timed exercise countdown (`practice-timer.js`) with explicit start and timeout auto-submit.
- Best elapsed time on timed passes with retry support.
- Docs: [progress.md](../docs/progress.md), [phase-3-manual-test-plan.md](../docs/phase-3-manual-test-plan.md).

## Approved deviations

| Topic | PRD / plan | Shipped |
|-------|------------|---------|
| Linear issue IDs | Plan TIM-38–TIM-42 | Created as TIM-42, TIM-41, TIM-38, TIM-39, TIM-40 (same milestone order) |
| Timer state | Session-scoped reset on navigate away | As planned; documented in manual test plan |

## Future work

- Accounts and cross-device progress sync.
- AI grading and explanations.
- Multi-exercise timed interview sessions.
- Align exercise prompts/sample SQL with `reference_sql` where still drifted (carried from Phase 2).

## Open questions

- None blocking; accounts vs local progress resolved in favor of cookies for Phase 3.
