# Phase 2 SQL execution and exact grading PRD

## Status

Draft for review. The user approved the direction in planning (2026-06-08). Do not create implementation issues or write application code until this PRD is approved and a scoped implementation plan from local `implement-from-prd` is approved.

## Source context

This phase follows the SQL Gym product vision in `prd/00-product-vision.md`, especially core loop steps 4–6: complete a SQL exercise, receive grading feedback, and see an attempt result.

Phase 1 in `prd/phase-1-dataset-exercise-catalog.md` delivered catalog models, 50 Times Archive exercises, practice-flow browsing, exercise previews, and placeholder-honest UI. SQL execution, grading, accounts, and durable progress remain out of scope.

Current implementation context:

- `src/app/catalog/` — JSON-backed exercise catalog (`TIMES_ARCHIVE_CATALOG`, 50 entries).
- `src/app/practice.py` — catalog filters and exercise preview context; disabled SQL editor placeholder on preview pages.
- `templates/practice_exercise.html` — exercise metadata, hints, sample SQL in `<details>`, placeholder editor and grading copy.
- `src/app/domain/exercises.py` — `ExpectedResultSpec` reserved for future exact-result fields.
- `src/app/domain/attempts.py` and `grading.py` — demo-only placeholders (`DEMO_ATTEMPT`, `GRADING_PLACEHOLDER`).
- `src/app/fixtures/times/archive_articles_demo.json` — two schema-aligned demo rows only.
- `templates/index.html` — Phase 0 home shell copy; does not yet reflect Phase 1 catalog capabilities.

## Resolved product decisions (planning, 2026-06-08)

- **Times article data:** load a Times export from [`times-api`](https://github.com/mikael-lh/times-api) into the practice database (replace demo-row-only fixture for query execution).
- **Execution database:** PostgreSQL, provisioned locally via **Docker Compose** checked into this repo.
- **Grading model (Phase 2):** **strict grid match** only — same columns (names and order), same rows (values and order); no partial credit.
- **Attempt persistence:** **session-only** for Phase 2 (no accounts, no durable attempt history).
- **SQL editor:** **CodeMirror 6** on exercise preview pages (not plain textarea).
- **Home page:** refresh `/` to reflect Phase 1 catalog and Phase 2 execution/grading boundaries honestly (not a new standalone catalog route).

## Problem

Learners can browse and preview 50 Times Archive exercises, but they cannot run SQL or receive correctness feedback. The underlying article data is still a two-row demo fixture, so even a prototype executor would not support realistic practice. The product vision’s core loop stops at placeholders for editor, grading, and progress.

## Goals

- Load production Times Archive article rows from a `times-api` export into PostgreSQL for learner queries.
- Let learners write and run PostgreSQL on exercise preview pages using CodeMirror.
- Grade a defined pilot set of exercises with strict grid-match comparison against stored expected results.
- Show clear pass/fail feedback and preserve placeholder honesty for capabilities still deferred (AI grading, accounts, durable progress, timed scoring).
- Keep execution and grading boundaries testable with focused PRs and documented local setup (Docker Compose).
- Refresh the home page so new users can discover the practice catalog and understand what works in Phase 2.

## Non-goals

- AI grading, explanations, or partial credit.
- User authentication, accounts, or cross-session personalization.
- Durable progress, attempt history, or database-backed learner state beyond the practice database dataset tables.
- Timed-mode scoring or interview timers.
- Grading all 50 exercises in the first Phase 2 slice (pilot subset is acceptable if requirements and tests cover the pattern).
- Scheduled or automated Times refresh beyond a documented import path for developers.
- Non-developer exercise authoring tooling.
- Arbitrary user-uploaded datasets.
- Standalone catalog route (catalog stays in `/practice`).

## Users and use cases

### Learner

As a learner, I want to run my SQL against real Times article data so practice feels realistic.

As a learner, I want to know whether my query result exactly matches the expected answer for gradable exercises.

As a learner, I want the app to be honest about what still does not work (AI feedback, saved progress across visits, timed scoring).

### Reviewer

As a reviewer, I want Docker-based setup and validation commands so I can reproduce execution and grading locally.

As a reviewer, I want grading rules documented and strict so pass/fail is deterministic.

### Future implementer

As a future implementer, I want session-only attempts and a clear execution layer so persistence and AI grading can be added without rewriting the editor or importer.

## Requirements

### R1. Times data in PostgreSQL via Docker Compose

The app must run learner SQL against Times Archive article rows stored in PostgreSQL, loaded from a `times-api` export.

Acceptance criteria:

- The repo includes Docker Compose configuration to start PostgreSQL for local development and agent environments.
- Database connection settings are documented in `.env.example` (no committed secrets).
- A documented import path loads Times article data from `times-api` into a schema aligned with `times-api/schema/archive_articles.json` (or the current canonical archive schema in that repo).
- `TIMES_ARCHIVE_CATALOG_DATASET` provenance and docs reference the Docker-backed data path rather than the two-row demo JSON as the execution source of truth.
- Import/setup steps are documented in README or a linked dev doc (e.g. `docs/times-data-setup.md`).
- Tests or validation scripts verify the imported row count is above the Phase 1 demo size and that required columns exist for pilot exercises.

### R2. SQL execution on exercise preview

Learners must be able to run PostgreSQL on the exercise preview page against the Times practice database.

Acceptance criteria:

- Exercise preview at `/practice/{dataset_id}/{exercise_id}` includes a CodeMirror 6 SQL editor (replacing the disabled textarea placeholder for gradable flow).
- Learners can run or submit SQL from the preview page; errors (syntax, permissions, timeouts) surface as clear, non-technical messages where practical.
- Execution uses the dataset’s target dialect (PostgreSQL only in Phase 2).
- Queries run with safety limits: read-only database role for learner execution, statement timeout, and row limit appropriate for practice (exact values documented).
- Learners cannot mutate practice data, create objects, or access non-practice schemas.
- UI copy states that only PostgreSQL against the Times practice database is supported.

### R3. Strict grid-match grading (pilot exercises)

The app must grade submitted results for a documented pilot set of catalog exercises using strict grid match.

Acceptance criteria:

- For each pilot exercise, expected results are defined in catalog or companion data using `ExpectedResultSpec` (and any companion grid payload required for strict match).
- **Strict grid match** means: identical column names and order, identical row count, identical cell values in row order (including NULL representation as defined in the grading spec).
- Grading returns pass or fail with a concise summary; no partial credit in Phase 2.
- Exercises outside the pilot set may remain run-only or show “grading not configured yet” without implying failure.
- Grading does not execute learner SQL twice in ways that cause flaky comparisons unless documented; comparison uses deterministic result capture.
- Tests cover pass case, fail case (wrong values, wrong row count, wrong column order), and exercises without expected results.

### R4. Session-only attempts and feedback

Attempt state for Phase 2 lives in the session only.

Acceptance criteria:

- A learner can submit SQL, receive execution output, and see grading feedback during the same browser session without creating an account.
- Attempt state does not require a learner database table in Phase 2.
- Refreshing the session or expiring the session may reset attempt state; UI or docs state that progress is not persisted across visits.
- Domain models in `attempts.py` and `grading.py` reflect real statuses for the session flow (`submitted`, `graded`, pass/fail) rather than demo-only placeholders on gradable paths.
- Static demo progress metrics remain demo-labeled or are hidden on gradable exercise previews so they do not imply durable tracking.

### R5. Placeholder honesty and home page

UI and docs must reflect Phase 2 capabilities and remaining boundaries.

Acceptance criteria:

- Exercise preview and practice pages clearly distinguish: SQL execution works (Phase 2), grading works for pilot exercises, AI grading / accounts / durable progress / timed scoring do not.
- `/` home page is updated to describe Phase 1 catalog + Phase 2 execution/grading and link learners into `/practice` (no standalone catalog route).
- README Phase 2 behavior section is updated when implementation lands (may be deferred to the docs milestone).
- `./scripts/validate-env.sh` remains the full local validation entry point; Phase 2 adds documented checks for Docker/DB where feasible without blocking contributors who skip execution locally (document any optional vs required checks).

### R6. Developer and reviewer workflow

Execution and grading work must be testable and reviewable in small PRs.

Acceptance criteria:

- Tests cover execution error handling, grading comparison logic, and key page flows (editor present, submit path, feedback rendering) using test doubles or fixtures where a live database is impractical in unit tests.
- Integration tests or a documented manual test plan cover end-to-end run + grade against Docker Postgres.
- Ruff, mypy, and pytest remain green; new modules follow existing `src/app/` layout conventions.

## Edge cases and error states

- Database not running: clear setup message pointing to Docker Compose docs.
- Empty or whitespace-only SQL: validation error before execution.
- Query timeout or row limit exceeded: user-friendly error; no partial grading.
- SQL syntax error: show database error message sanitized for learners.
- Non-`SELECT` statements (if disallowed): reject with clear policy message.
- Exercise without expected result payload: run allowed; grading unavailable message (not a fail).
- Strict match on floating-point or type formatting: define comparison rules in implementation plan (prefer exact types from PostgreSQL result sets; document NULL vs empty string).
- Session lost: attempt state reset; no error crash.
- Unknown dataset/exercise routes: existing Phase 1 404 behavior preserved.

## Out of scope for Phase 2

- AI-assisted grading or natural-language explanations.
- Accounts, login, or cross-device progress.
- Durable attempt storage in PostgreSQL or other DB tables for learners.
- Timed-mode timers, scoring, or leaderboards.
- Grading every catalog exercise (pilot subset required; expand later).
- Automated scheduled refresh from `times-api`.
- Monaco editor (CodeMirror 6 is the chosen editor).
- CI provisioning of Docker Postgres unless separately approved (document local/agent setup first).

## Success signals

Phase 2 is successful when a reviewer can:

- Run `docker compose up` (or documented equivalent), import Times data, and start the app with a valid `DATABASE_URL`.
- Open a pilot exercise preview, write SQL in CodeMirror, run it against real Times rows, and submit for grading.
- See strict pass/fail feedback that matches documented grid-match rules.
- Confirm session-only behavior (no account, no persisted history across a fresh session).
- Land on an updated home page that routes them to `/practice` with accurate capability copy.
- Run documented validation commands successfully.

## Open questions

- **times-api export pin:** which commit, archive file, or export command is canonical for Phase 2 imports?
- **Pilot exercise count:** how many of the 50 exercises must ship with expected results in the first release (suggest 5–10 representative exercises across difficulties)?
- **Table naming:** confirm learner-facing table name(s) in Postgres (e.g. `times_archive`) match exercise prompts and sample SQL.
- **CodeMirror delivery:** CDN vs vendored static assets (implementation plan should pick one for offline/agent use).
- **Session mechanism:** Starlette session middleware vs signed cookie payload (implementation plan decides).
- **Optional validate-env:** whether `./scripts/validate-env.sh` requires Docker Postgres or treats DB checks as optional when `DATABASE_URL` is unset.

## Approval

Pending user review of this draft PRD. After approval:

1. Update `prd/README.md` to name Phase 2 as the active phase.
2. Run `implement-from-prd` for a scoped implementation plan and Linear issues.
3. Implement only after the plan is approved.
