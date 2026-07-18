# Phase 6 reliability and code-quality PRD

## Status

**Draft — not approved, not active.** Awaiting user approval before it becomes the active phase and before any implementation plan or code is written.

This phase changes **how the code is built**, not what the product does. With one small exception (a query-blocking bug fix in R2), learners should not see any behavior change. The goal is a more reliable app and a cleaner, easier-to-work-in codebase.

## Source context

Follows `prd/00-product-vision.md` and comes after `prd/phase-5-console-workspace.md` (the current shipped behavior).

Phase 5 delivered the single practice workspace. Since Phases 0–5 were built incrementally, the codebase has accumulated some leftover/duplicated code and a few reliability rough edges. This phase is a focused clean-up and hardening pass, grounded in a code review of `src/app/`, `static/js/`, and `templates/`.

No new product features. No new datasets. No new screens.

## Problem

Three kinds of issues make the app less reliable and the code harder to change safely:

1. **Reliability rough edges.** The way the app talks to the database and protects itself can fail under real use (many users at once, real-world data, or a missing production setting).
2. **Duplicated code.** The same logic is copy-pasted in two or three places, so a change in one spot can silently disagree with the others.
3. **Dead code.** Leftover pieces from earlier phases are still shipped but no longer used, which makes the project bigger and more confusing than it needs to be.

## Goals

- Make SQL execution more reliable under concurrent use.
- Make the "read-only queries only" safety net actually reliable, and stop it from wrongly rejecting valid learner queries.
- Fail safely if the app is deployed without a real signing secret.
- Remove duplicated logic so there is a single source of truth.
- Delete unused leftover code so the codebase reflects what actually ships.
- Improve readability of the biggest/most tangled files.
- Keep learner-visible behavior the same (except the R2 bug fix, which unblocks valid queries).

## Non-goals

- Accounts, authentication, or cross-device sync.
- AI grading, hints, or partial credit.
- New datasets, exercises, or screens.
- Visual/design redesign of the workspace.
- Rewriting the app in a different framework or language.

## Users and use cases

Same users as today: learners practicing SQL in the workspace. This phase does not add a use case; it protects the existing ones (Run SQL, Submit for grading, switch exercises, track progress) from breaking under load, bad input, or misconfiguration.

## Requirements

Each requirement below has a **plain-language** explanation of what it means and why it matters.

### Reliability

#### R1. Reuse database connections (connection pooling)

**Plain-language:** Right now the app opens a brand-new connection to the database every time someone clicks **Run** or **Submit**, then throws it away. Opening a connection is slow, and if several people use the app at once the database can run out of connection slots and start refusing queries. A "connection pool" keeps a small set of connections open and reuses them.

- Introduce a shared connection pool for learner query execution (created once when the app starts, closed when it stops).
- `execute_query` (`src/app/execution/execute.py`) borrows a connection from the pool instead of calling `psycopg.connect(...)` per query.
- The per-query statement timeout and row limits stay exactly as they are today.

Acceptance criteria:
- Repeated Run/Submit calls reuse pooled connections rather than opening a new one each time.
- Existing execution tests still pass; a test confirms concurrent queries succeed without exhausting connections.
- Timeout and 500-row limit behavior is unchanged.

#### R2. Make "read-only only" safety reliable, and stop false rejections

**Plain-language:** The app tries to ensure learners can only run read (`SELECT`) queries by scanning the query text for banned words like `DELETE`, `DROP`, and for extra semicolons. Two problems: (a) the practice data is real news text, so a valid query that searches for an article containing a word like "create" or "delete", or a headline containing a semicolon, can get **wrongly blocked**; (b) text-scanning is not a real guarantee. The stronger approach is to tell the **database itself** to refuse any write, so safety doesn't depend on guessing from the text.

- Execute every learner query inside a **read-only database transaction** so the database rejects any write regardless of the text.
- Keep a lightweight text check only as a friendly upfront message (e.g. "enter a query", "only SELECT is allowed"), not as the sole safety mechanism.
- Fix the false-rejection cases: valid `SELECT` queries whose **string values** contain banned words or semicolons must run successfully.
- Keep relying on the read-only database role documented in `.env.example` and `docker/postgres/init/02-roles.sql` as defense in depth.

Acceptance criteria:
- A write query (e.g. `DELETE ...`) is rejected even if the text check were bypassed (proven by a test that runs against the read-only transaction).
- A valid `SELECT` containing a banned word inside a quoted string (e.g. `WHERE headline = 'plans to create jobs'`) runs and returns rows.
- A valid `SELECT` containing a semicolon inside a quoted string runs successfully.
- Existing SELECT-only tests still pass.

#### R3. Fail safely without a production signing secret (and de-duplicate it)

**Plain-language:** The app signs its cookies (session + the 60-day progress cookie) with a secret key. If that key isn't set in production, the code currently falls back to a default value that's written right here in this public repo — meaning someone could forge a cookie and tamper with progress. Also, that fallback code is copy-pasted in two files, so they can drift apart.

- One shared place returns the signing secret (used by both `src/app/main.py` and `src/app/progress/cookie.py`).
- In development, the dev fallback secret is fine. When the app is run in production without `SESSION_SECRET` set, it should refuse to start (or emit a loud, unmistakable warning) rather than silently use the public default.

Acceptance criteria:
- The default secret string exists in exactly one place in the code.
- Starting the app in a production configuration without `SESSION_SECRET` fails fast or logs a clear warning (behavior decided in the implementation plan; see Open questions).
- Development startup is unchanged.

### Remove duplicated logic

#### R4. One place that turns results/errors/grading into JSON

**Plain-language:** The code that converts a query result, an error, or a grading outcome into the JSON the browser reads exists twice — in `src/app/api/practice.py` and `src/app/practice_session.py` — with slightly different behavior (one caps rows at 25, the other doesn't). Two near-identical copies invite bugs when only one is updated.

- Consolidate these serializers into a single module.
- The 25-row preview cap becomes an explicit option/argument, so the difference is obvious instead of hidden in a duplicate.

Acceptance criteria:
- Only one implementation of each serializer remains.
- Full-result responses and 25-row session previews both behave exactly as they do today.

#### R5. One source of truth for progress labels

**Plain-language:** The mapping from a status (`not_started`, `attempted`, `passed`) to its display text ("Not started", "Attempted", "Passed") is written three times — twice in Python and once in JavaScript. They can disagree.

- Define these labels once on the server and reuse them; the browser uses the label the server already sends instead of re-deriving it.

Acceptance criteria:
- The label mapping is defined once server-side.
- Badges and status text look identical to today.

#### R6. One helper for elapsed-time formatting (frontend)

**Plain-language:** Turning a number of seconds into `M:SS` is implemented in a few spots in the workspace JavaScript. One small helper avoids drift.

- Single JavaScript helper for `M:SS` formatting, reused where needed.

Acceptance criteria:
- Timer and "solved in" text display identically to today.

### Remove dead code

#### R7. Delete leftover code from earlier phases

**Plain-language:** Several pieces were built for Phases 0–4 and are no longer used by the running app — some are only kept alive by their own tests. Removing them (and their tests) makes the project smaller and clearer, with no user-visible effect.

Candidates identified in review (implementation plan to confirm none are imported elsewhere before deleting):
- `static/js/practice-timer.js` — an entire countdown-timer file that no template loads.
- `resolve_workspace_exercise` in `src/app/workspace/navigation.py`.
- `continue_exercise_url` in `src/app/progress/navigation.py`.
- `ProgressSummary`, `ProgressMetric`, `build_progress_summary`, `DEMO_PROGRESS` in `src/app/domain/progress.py`.
- `Attempt` and `DEMO_ATTEMPT` in `src/app/domain/attempts.py`.
- `GRADING_PLACEHOLDER` in `src/app/domain/grading.py`.
- `TIMES_ARCHIVE_PLACEHOLDER_EXERCISE` in `src/app/domain/exercises.py`, plus `TIMES_ARCHIVE_DEMO_DATASET` and the unused `src/app/fixtures/times/archive_articles_demo.json` fixture.
- Any CSS in `static/styles.css` tied only to removed elements (e.g. `.editor-form`).

Acceptance criteria:
- Each item is confirmed unused by the running app before removal.
- Tests that only existed to cover removed code are removed with it.
- `./scripts/validate-env.sh` (build, ruff, mypy, pytest) stays green.

### Readability and structure

#### R8. Simplify the route wiring

**Plain-language:** In `src/app/main.py`, each API route is a small wrapper function that just calls another function. This is extra boilerplate that makes the list of routes harder to read.

- Reduce the pass-through wrappers (e.g. register handlers directly and/or group routes into an `APIRouter`), and remove the duplicated 404 rendering in the exercise route.

Acceptance criteria:
- Same URLs, same responses, same status codes as today (covered by existing route tests).
- Fewer lines / less boilerplate in `main.py`.

#### R9. Give the workspace page a typed data object

**Plain-language:** The workspace page is handed a big loose dictionary of ~40 keys, with some values repeated. A typed object makes it clear what the page needs and catches typos automatically.

- Replace the loose `dict[str, object]` from `get_workspace_context` (`src/app/workspace/context.py`) with a typed structure, removing the duplicated top-level vs. nested values.

Acceptance criteria:
- The workspace and the JSON API render the same content as today.
- Type checking (mypy) passes and would catch a missing/renamed field.

#### R10. Split the large workspace JavaScript file

**Plain-language:** `static/js/practice-workspace.js` is one ~830-line file doing many jobs (rendering, the timer, navigation, the drawer, network calls). Splitting it into a few smaller files makes each part easier to read and change.

- Break the file into focused modules (e.g. rendering, stopwatch, navigation, API client) with no behavior change.

Acceptance criteria:
- Workspace behavior (run, submit, switch, drawer, timer, modal) is unchanged.
- Existing browser/layout tests still pass.

### Docs and validation

#### R11. Update docs and keep checks green

- Update `README.md` and `docs/session-state.md` where wording no longer matches the code after clean-up.
- Add a short `docs/phase-6-manual-test-plan.md` covering the run/submit happy path, the R2 false-rejection fix, and progress tracking.
- `./scripts/validate-env.sh` and `uv run pytest` pass.

## Phase acceptance criteria

- [ ] Database connections are pooled and reused; timeout/row limits unchanged.
- [ ] Read-only safety is enforced by the database; valid `SELECT`s with banned words or semicolons inside strings run correctly.
- [ ] App fails safely (or warns loudly) in production without `SESSION_SECRET`; the default secret lives in one place.
- [ ] Serializers, progress labels, and time formatting each have a single source of truth.
- [ ] Confirmed-unused leftover code and its tests are removed; validation stays green.
- [ ] Route wiring simplified; workspace context typed; large JS file split — all with no user-visible change.
- [ ] Docs updated; Phase 6 manual test plan added.

## Edge cases and error states

| Case | Expected behavior |
|------|-------------------|
| Database temporarily unavailable | Clear "database unavailable" message (as today); pool recovers when the database returns |
| Many concurrent Run/Submit calls | Queries succeed by reusing pooled connections; no connection-exhaustion errors |
| Valid `SELECT` with a banned word inside a string | Runs and returns rows (no false rejection) |
| Actual write attempt (e.g. `UPDATE`) | Rejected by the read-only transaction |
| Production start without `SESSION_SECRET` | Fails fast or logs a loud warning (final choice in implementation plan) |
| A "dead code" item turns out to be imported somewhere | It is kept, not deleted; only confirmed-unused code is removed |

## Out of scope

- Any new learner-facing feature or content.
- Changing grading rules or the strict grid-match logic.
- Live schema introspection (schema still comes from the checked-in fixture).
- Performance work beyond connection pooling.

## Success signals

- The app handles several simultaneous users without database connection errors.
- Learners are no longer blocked by valid queries that happen to contain a keyword or semicolon in text.
- The codebase is smaller (dead code gone) and each piece of logic lives in one place.
- Future changes are easier and safer because there are fewer duplicates and clearer types.
- No regression in existing tests or learner-visible behavior.

## Open questions

- **Secret handling (R3):** should the app hard-fail on startup without `SESSION_SECRET` in production, or start with a loud warning? Needs a product/ops call.
- **How to detect "production" (R3):** by an explicit env var (e.g. `APP_ENV=production`) or another signal? To be settled in the implementation plan.
- **PR sizing:** per `.cursor/rules/engineering.mdc` (small, focused PRs), these likely ship as several PRs (reliability, de-duplication, dead-code removal, structure). Confirm you want them split rather than one large change.
- **Scope trimming:** if you'd prefer the smallest first step, R2 (query bug fix) + R7 (dead code) + R3 (secret) give the most value for the least risk; R8–R10 could be deferred.

## Approval

- [ ] PRD scope approved by user.
- [ ] Phase 6 named active in `prd/README.md` (only after approval).
- [ ] Implementation plan approved (via `implement-from-prd`) before any code changes.

## References

- `prd/00-product-vision.md`
- `prd/phase-5-console-workspace.md`
- `.cursor/rules/engineering.mdc`, `.cursor/rules/workflow.mdc`
- `src/app/execution/execute.py`, `src/app/execution/sql_sanitize.py`
- `src/app/api/practice.py`, `src/app/practice_session.py`
- `src/app/main.py`, `src/app/progress/cookie.py`, `src/app/workspace/context.py`
- `src/app/domain/progress.py`, `src/app/domain/attempts.py`, `src/app/domain/grading.py`, `src/app/domain/exercises.py`
- `static/js/practice-workspace.js`, `static/js/practice-timer.js`
- `docker/postgres/init/02-roles.sql`, `.env.example`
