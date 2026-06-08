# Phase 2 implementation plan

## Status

Draft for user approval. Do not write application code outside the scoped Linear issue being implemented.

## Source

- PRD: `prd/phase-2-sql-execution-grading.md`
- Linear epic: `TIM-30` _(proposed; create after plan approval)_
- Child issues: `TIM-31`, `TIM-32`, `TIM-33`, `TIM-34`, `TIM-35`, `TIM-36`

## Planning decisions

- **Postgres via Docker Compose:** `docker-compose.yml` at repo root; practice DB on port `5432` (document overrides).
- **times-api import:** `scripts/import-times-from-times-api.sh` downloads a **pinned** export from [`times-api`](https://github.com/mikael-lh/times-api) (commit hash documented in `docs/times-data-setup.md`) and loads rows into Postgres. Pin is updated deliberately when the archive export changes.
- **Learner table name:** `times_archive` (matches existing exercise `sample_sql` and prompts).
- **Execution driver:** `psycopg` (v3) with a small sync execution module; keep routes server-rendered (HTML forms), not a separate JSON API.
- **Safety:** `sql_gym_readonly` DB role; `statement_timeout` (e.g. 5s); `max_rows` cap (e.g. 500); **SELECT-only** statements rejected at app layer before execution; no DDL/DML for learners.
- **Grading:** **strict grid match** on column names/order, row count, and cell values in row order; `NULL` vs empty string compared as Postgres returns them (document in `docs/grading.md`).
- **All 50 exercises:** each exercise gets `reference_sql` (canonical answer query) plus a committed `expected_grid` payload generated from that query against imported data.
- **Expected-result authoring:** `scripts/generate-expected-results.sh` runs `reference_sql` for each exercise via admin DB connection and writes grids into catalog data; CI/tests verify 50/50 exercises have non-empty grids.
- **CodeMirror:** vendored static assets under `static/vendor/codemirror/` (no CDN; works offline and in Cloud Agents).
- **Session:** Starlette `SessionMiddleware` with `SESSION_SECRET` from env; session holds latest attempt/grading per exercise id only.
- **validate-env:** Postgres checks are **optional** when `DATABASE_URL` is unset; documented in README.
- **Non-goals:** AI grading, accounts, durable learner DB tables, timed scoring, Monaco, CI Docker (unless separately approved).

## Milestones

### 1. `TIM-31` — Docker Postgres and Times import

**Goal:** Provision PostgreSQL and load real Times Archive rows from `times-api`.

**Files to create or modify:**

- `docker-compose.yml` — Postgres service, volume, healthcheck.
- `docker/postgres/init/` — schema for `times_archive`, readonly role, app role grants.
- `scripts/import-times-from-times-api.sh` — download pinned export, load into DB.
- `docs/times-data-setup.md` — setup, pin, import, troubleshooting.
- `.env.example` — `DATABASE_URL`, `SESSION_SECRET`, optional admin URL for import.
- `src/app/domain/datasets.py` — provenance note points at Docker/import path.
- `tests/test_times_import.py` — row-count/column checks (skip if no `DATABASE_URL`).

**Implementation notes:**

- Map `times-api` archive schema (`schema/archive_articles.json`) to Postgres types; JSON columns for `keywords`, `byline_person`, `multimedia_count_by_type`.
- Importer is idempotent (`TRUNCATE` + reload or upsert).
- Confirm export artifact path in `times-api` during this milestone (spike subtask); document pin in `docs/times-data-setup.md`.

**Acceptance criteria covered:** R1 (all), partial R6 (integration test hook).

**Checks:** `docker compose up -d`, import script, optional `uv run pytest tests/test_times_import.py`, `uv run ruff check .`, `uv run mypy .`.

**Risks:** Export file location/size in `times-api`; large imports slow first-time setup.

---

### 2. `TIM-32` — Expected results for all 50 exercises

**Goal:** Every catalog exercise has gradable expected-result data.

**Files to create or modify:**

- `src/app/domain/exercises.py` — extend `ExpectedResultSpec` with `reference_sql` and `expected_grid` (columns + rows); catalog loader validation.
- `src/app/catalog/data/times_exercises.json` — add `reference_sql` per exercise (initially canonicalize from current `sample_sql` where appropriate).
- `src/app/catalog/data/expected_grids/` or embedded grids in JSON — committed grid payloads.
- `scripts/generate-expected-results.sh` — regenerate grids from DB using `reference_sql`.
- `tests/test_domain.py` — all 50 exercises have `reference_sql` and grid; catalog rejects missing grids.

**Implementation notes:**

- `reference_sql` is the authoritative query for grading (may differ from hint `sample_sql`).
- Grid format: `{ "columns": ["col", ...], "rows": [[val, ...], ...] }` with JSON-null for SQL NULL.
- Generation script requires Docker DB from TIM-31; document in `docs/times-data-setup.md`.
- Review exercises whose `sample_sql` uses `LIMIT` or non-deterministic ordering — `reference_sql` must be deterministic for stable grids.

**Acceptance criteria covered:** R3 (data + validation), partial R6.

**Checks:** `uv run pytest tests/test_domain.py`, generation script dry-run docs, ruff, mypy.

**Risks:** Non-deterministic queries across 50 exercises; content review for `reference_sql` quality.

---

### 3. `TIM-33` — SQL execution layer

**Goal:** Execute learner SELECT queries safely against practice Postgres.

**Files to create or modify:**

- `pyproject.toml` — add `psycopg[binary]`.
- `src/app/db/` — connection helpers, settings from `DATABASE_URL`.
- `src/app/execution/` — `execute_query(sql) -> QueryResult` with timeout/row limits, SELECT-only guard, sanitized errors.
- `tests/test_execution.py` — unit tests with mocked cursor; optional integration marker.

**Implementation notes:**

- `QueryResult` captures column names, rows, row count, truncated flag.
- DB unavailable → structured error for UI (“start Docker Postgres — see docs”).
- No learner-facing connection string exposure.

**Acceptance criteria covered:** R2 (backend), R6 (tests), edge cases (empty SQL, timeout, syntax error).

**Checks:** `uv run pytest tests/test_execution.py`, ruff, mypy.

**Risks:** SQL injection — use parameterized separation; only pass learner SQL as single statement; readonly role as defense in depth.

---

### 4. `TIM-34` — Strict grid-match grading

**Goal:** Compare execution results to expected grids with pass/fail outcomes.

**Files to create or modify:**

- `src/app/grading/strict_match.py` — `grade(result, expected_grid) -> GradingOutcome`.
- `src/app/domain/grading.py` — real statuses (`graded`), `passed: bool`, summary messages.
- `src/app/domain/attempts.py` — session-oriented attempt states (`submitted`, etc.).
- `docs/grading.md` — strict match rules, NULL handling, type formatting.
- `tests/test_grading.py` — pass, wrong values, wrong row count, wrong column order, NULL cases.

**Implementation notes:**

- Single execution per submit; grade compares captured result (no second run).
- Fail summaries are learner-safe (“column order does not match”, “row count differs”) without leaking answers.

**Acceptance criteria covered:** R3 (logic), R6.

**Checks:** `uv run pytest tests/test_grading.py`, ruff, mypy.

**Risks:** Postgres type formatting (dates, decimals) — compare using stringified cell values from psycopg consistently.

---

### 5. `TIM-35` — CodeMirror editor, session, run/submit UI

**Goal:** Replace placeholder editor with interactive run/grade on exercise preview.

**Files to create or modify:**

- `static/vendor/codemirror/` — vendored CodeMirror 6 bundles.
- `static/js/practice-editor.js` — init editor, sync to form field.
- `src/app/main.py` — `SessionMiddleware`; POST routes for run-only and submit-grade on preview path.
- `src/app/practice.py` — session attempt helpers; wire execution + grading.
- `templates/practice_exercise.html` — CodeMirror, run/submit forms, result table, pass/fail feedback; hide demo progress block.
- `templates/practice.html` — update placeholder copy for execution availability.
- `static/styles.css` — editor layout, result table, feedback states.
- `tests/test_app.py` — editor assets present, POST flow with mocked execution/grading.

**Implementation notes:**

- Server-rendered POST + redirect/re-render pattern (no SPA).
- Session stores `{exercise_id: {sql, result, grading}}` for current visit.
- Run shows result grid without grading; Submit runs + grades.
- UI copy: session-only, no AI, no durable progress.

**Acceptance criteria covered:** R2 (UI), R4, partial R5 (preview copy).

**Checks:** `uv run pytest tests/test_app.py`, manual browser check, ruff, mypy.

**Risks:** CodeMirror bundle size; form CSRF not required for local MVP but note in docs.

---

### 6. `TIM-36` — Home page, docs, and validation

**Goal:** Align home/README/validate-env with Phase 2 reality.

**Files to create or modify:**

- `templates/index.html` — Phase 1 catalog + Phase 2 execution/grading CTA to `/practice`.
- `src/app/main.py` — update home context strings and placeholder list.
- `README.md` — Phase 2 behavior, Docker setup link, optional DB validation note.
- `tests/test_developer_workflow.py` — guard new README strings.
- `scripts/validate-env.sh` — optional Postgres ping when `DATABASE_URL` set.
- `docs/phase-2-manual-test-plan.md` — end-to-end run + grade checklist.

**Implementation notes:**

- `./scripts/validate-env.sh` remains the main validation entry; DB check does not fail when unset.
- Integration test or manual plan covers Docker + one pass + one fail exercise.

**Acceptance criteria covered:** R5 (all), R6 (integration/manual).

**Checks:** `uv run pytest`, `./scripts/validate-env.sh`, `git diff --check`.

**Risks:** Docs drift — guard high-signal README claims in tests.

---

## Requirement coverage

| PRD item | Covered by |
|----------|------------|
| R1. Times data in PostgreSQL via Docker Compose | `TIM-31` |
| R2. SQL execution on exercise preview | `TIM-31` (data), `TIM-33`, `TIM-35` |
| R3. Strict grid-match grading (all 50) | `TIM-32`, `TIM-34` |
| R4. Session-only attempts and feedback | `TIM-35` |
| R5. Placeholder honesty and home page | `TIM-35` (preview), `TIM-36` |
| R6. Developer and reviewer workflow | all milestones; `TIM-36` |

## Out of scope (explicit)

- AI grading, accounts, durable attempt tables, timed scoring, automated Times refresh, Monaco, non-developer authoring, standalone `/catalog`, CI Postgres.

## Engineering principles check

| Principle | Assessment |
|-----------|------------|
| Minimal scope per PR | Six focused milestones; one Linear issue each. |
| Design fit | Execution and grading layers separate from catalog and templates; matches Phase 1 layout. |
| Simplicity | Server-rendered forms, sync psycopg, vendored CodeMirror — no SPA or ORM. |
| DRY | Reuse catalog loader, practice context, existing domain models. |
| Tests | Unit tests with mocks for execution/grading; optional integration for DB. |
| Small CLs | Expected-result generation may be a large data diff — single milestone, reviewable by validation tests. |

**Non-blocking trade-offs:**

- Sync psycopg blocks worker briefly — acceptable for local MVP traffic.
- Large `times_exercises.json` / grid files — acceptable for 50 exercises; split grid files if diff noise is high.

## Blocked / resolve during TIM-31

- **times-api export pin:** confirm exact file URL/path in `times-api` repository (required before import script is final).

## Approval

Pending user approval of this plan. After approval:

1. Merge Phase 2 PRD if not already on `main`.
2. Update `prd/README.md` to name Phase 2 as active.
3. Create Linear epic `TIM-30` and child issues `TIM-31`–`TIM-36`.
4. Implement one issue at a time via `sql-gym-implement-issue` (or authorized `sql-gym-run-phase`).
