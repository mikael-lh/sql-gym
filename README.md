# sql-gym

A lightweight gym for SQL: practice on curated datasets, run queries, and level up by concept and difficulty.

## Status

**Phase 5 complete** — single practice workspace with in-page run/submit console, exercise drawer, and JSON APIs ([prd/phase-5-console-workspace.md](prd/phase-5-console-workspace.md)). Phase 4–0 behavior below remains unless superseded in the Phase 5 PRD. New product scope requires a new phase PRD plus an approved implementation plan.

| | |
|--|--|
| Full workflow reference | [docs/WORKFLOW.md](docs/WORKFLOW.md) |
| Product specs | [prd/README.md](prd/README.md) |
| Phase 5 implementation plan | [docs/phase-5-implementation-plan.md](docs/phase-5-implementation-plan.md) |
| Session state | [docs/session-state.md](docs/session-state.md) |
| Phase 5 manual test plan | [docs/phase-5-manual-test-plan.md](docs/phase-5-manual-test-plan.md) |
| Phase 4 implementation plan | [docs/phase-4-implementation-plan.md](docs/phase-4-implementation-plan.md) |
| Phase 4 manual test plan | [docs/phase-4-manual-test-plan.md](docs/phase-4-manual-test-plan.md) |
| Phase 3 implementation plan | [docs/phase-3-implementation-plan.md](docs/phase-3-implementation-plan.md) |
| Progress cookie | [docs/progress.md](docs/progress.md) |
| Phase 3 manual test plan | [docs/phase-3-manual-test-plan.md](docs/phase-3-manual-test-plan.md) |
| Phase 2 implementation plan | [docs/phase-2-implementation-plan.md](docs/phase-2-implementation-plan.md) |
| Times data setup | [docs/times-data-setup.md](docs/times-data-setup.md) |
| Grading rules | [docs/grading.md](docs/grading.md) |
| Phase 2 manual test plan | [docs/phase-2-manual-test-plan.md](docs/phase-2-manual-test-plan.md) |
| Phase 1 implementation plan | [docs/phase-1-implementation-plan.md](docs/phase-1-implementation-plan.md) |
| Phase 0 implementation plan | [docs/phase-0-implementation-plan.md](docs/phase-0-implementation-plan.md) |
| Linear project | [sql-gym](https://linear.app/times-api/project/sql-gym-ce6a8985c99e) (`TIM-` issues) |

## Setup

SQL Gym uses Python 3.12, FastAPI, server-rendered templates, and [`uv`](https://docs.astral.sh/uv/) for dependency management. This keeps the scaffold close to the adjacent [`times-api`](https://github.com/mikael-lh/times-api) Python ecosystem while preserving a simple web app path for later SQL practice features.

**One-command local dev** (git pull, `.env`, deps, Postgres, Times import if needed, server, browser):

```bash
./scripts/dev.sh
```

Install dependencies:

```bash
uv sync
```

Run the development server:

```bash
uv run uvicorn app.main:app --reload
```

Production build:

```bash
uv build
```

This writes Python package artifacts to `dist/`: a source distribution (`.tar.gz`) and an installable wheel (`.whl`).

Lint, type-check, tests, and full repo validation: [Baseline validation checks](#baseline-validation-checks).

### Cursor Cloud Agents

Cloud environment hooks are version-controlled in [`.cursor/environment.json`](.cursor/environment.json):

- `scripts/cloud-env-bootstrap.sh` — idempotent VM bootstrap (`uv`, permissions)
- `scripts/cloud-env-update.sh` — per-session `uv sync --locked`

Cursor runs both via the `install` field on every agent startup (after `git pull`). See [Cloud environment setup](https://cursor.com/docs/cloud-agent/setup.md).

## Baseline validation checks

For TIM-21 and future scaffold PRs, reviewers and agents should run these checks from the repo root:

| Purpose | Command |
|---------|---------|
| Production package build | `uv build` |
| Lint | `uv run ruff check .` |
| Static type check | `uv run mypy .` |
| Test suite | `uv run pytest` |
| Full repo validation | `./scripts/validate-env.sh` |

`./scripts/validate-env.sh` wraps the build, lint, static check, and test commands above, then verifies the PRD/workflow files that future agents rely on. When `DATABASE_URL` is set, it also pings Postgres (optional; skipped when unset).

### Docker Postgres and Times data

```bash
cp .env.example .env
docker compose up -d
./scripts/import-times-from-times-api.sh
```

See [docs/times-data-setup.md](docs/times-data-setup.md) for GCS credentials and troubleshooting.

## Phase 5 behavior status

Working behavior:

- **`GET /practice/{dataset}/{exercise}`** workspace: schema, prompt, hint, objectives, editor, output console, drawer, prev/next.
- **Run/submit without page reload** via `/api/practice/...` JSON endpoints.
- Dismissible **grading modal** on submit; timed auto-submit uses the same API.
- In-place exercise switching (`fetch` + `history.pushState`) with session restore.
- Filter changes navigate to `/practice?difficulty=...&mode=...` then first eligible exercise.
- Legacy interview URLs redirect to `/practice`.

Placeholder behavior:

- Authentication, accounts, and cross-device sync.
- AI grading, explanations, and partial credit.

## Phase 4 behavior status

Shipped in Phase 4 and retained where not superseded by Phase 5:

- Session preview cap (25 rows) for wide result sets.
- Catalog copy aligned for date exercises `times-archive-011` and `times-archive-014`.

Removed in Phase 5:

- Interview session queues and `/practice/interview/...` UI (redirect only).
- Catalog card grid and per-exercise form POST run/submit pages.

## Phase 3 behavior status

Working behavior:

- Signed `sql_gym_progress` cookie (60-day lifetime) for pass/attempt badges without accounts.
- Catalog and home **Continue practicing** link (difficulty-aware on `/practice`).
- **Clear my progress** in the workspace via the JSON API.
- Per-exercise timed countdown on 16 `Timed` catalog exercises with timeout auto-submit.
- Best elapsed time recorded on timed passes (retries allowed).

Placeholder behavior:

- Authentication, accounts, and cross-device progress sync.
- AI grading, explanations, and partial credit.
- Standalone `/catalog` route (practice entry is `/practice` → workspace).

## Phase 2 behavior status

Working behavior:

- Docker Compose PostgreSQL with imported Times Archive rows (`times_archive` table).
- CodeMirror SQL editor on exercise preview pages with **Run SQL** and **Submit for grading**.
- Strict grid-match grading for all 50 catalog exercises.
- Learner-facing SELECT-only execution with timeout and row limits.
- Session cookie for draft SQL and last run/grade (browser session).

Placeholder behavior (superseded in Phase 3 where noted):

- Timed-mode scoring — **shipped in Phase 3** for per-exercise timers.
- Durable progress — **shipped in Phase 3** via browser cookie (not accounts).

## Phase 1 behavior status

Working behavior:

- Catalog domain models and validation for datasets and exercises.
- Production-ready Times Archive catalog dataset with 50 structured exercise entries.
- `/practice` catalog browsing with dataset, difficulty, and mode filters.
- `/practice/{dataset_id}/{exercise_id}` exercise preview pages linked from the practice flow.
- User-friendly 404 responses for unknown exercise preview routes.
- Inline empty states when practice filters return no exercises.
- Hints and sample SQL disclosure patterns that keep illustrative SQL hidden by default.

Historical note: Phase 1 shipped catalog browsing and exercise previews before Phase 2 added execution and grading on preview pages.

## Phase 0 behavior status

Working behavior:

- FastAPI app startup via `uv run uvicorn app.main:app --reload`.
- Server-rendered home and practice pages.
- `/health` returns a basic status response.
- Static stylesheet serving under `/static/`.
- Pydantic domain models for dataset, exercise, attempt, grading, and progress concepts.
- Baseline validation with `uv build`, ruff, mypy, pytest, and `./scripts/validate-env.sh`.

Historical placeholder behavior (superseded on `/practice` by Phase 1 catalog browsing):

- Single Times Archive demo dataset and one placeholder exercise on the practice shell before Phase 1 catalog work landed.

## Remaining follow-up decisions

- Production Times refresh automation beyond the documented GCS import path.
- Persistence: learner accounts, cross-device sync, and server-side attempt history (Phase 3 uses browser cookies only).
- Authentication and personalization.
- AI provider: explanations, hints, and partial credit beyond strict grid match.
- Timed-mode scoring behavior.

## Cursor setup

Install these Cursor integrations once (details in [WORKFLOW § Stack](docs/WORKFLOW.md#stack)):

- **Linear** (MCP) — backlog and issue status
- **GitHub** (MCP) — PRs, CI, authorized merges on cloud agents
- **Superpowers** — implementation and code review during builds
- **cursor-team-kit** (optional) — `deslop` pass on changed code

Specs, implementation plans, PRD alignment, and PRD updates use repo skills in [.cursor/skills](.cursor/skills). Connect Linear and GitHub in Cursor settings if MCP lookups fail.

## How we work

Specs live in **`prd/`**. Work is tracked in **Linear**, shipped via **GitHub PRs**, and built with **Cursor** repo skills (prompts below). You own product calls, plan sign-off, and merge by default; agents merge only when you explicitly authorize autonomous GitHub MCP merges. Agent gates: [.cursor/rules/workflow.mdc](.cursor/rules/workflow.mdc). Full playbook: [docs/WORKFLOW.md](docs/WORKFLOW.md) ([end-to-end flow](docs/WORKFLOW.md#end-to-end-flow)).

### Workflow

| Step | Your job | In Cursor |
|------|----------|-----------|
| **Requirements** | Approve specs; set the active phase in [prd/README.md](prd/README.md) | `write-prd` → commit under `prd/` |
| **Backlog** | Create Linear issues (`TIM-NN`) with a `prd/` link and acceptance criteria | — |
| **Plan** | Review and approve the phase implementation plan | `implement-from-prd` plus engineering-principles check |
| **Build** | Confirm the plan is approved | `sql-gym-implement-issue` for one `TIM-NN`, or `sql-gym-run-phase` for approved autonomous phase execution |
| **Pre-review** | Wait for the loop to finish; then review the PR yourself | **`sql-gym-pre-review`** for `TIM-NN` |
| **Ship** | Merge, close the Linear issue; assess `update-prd` after merged implementation | `update-prd` when PRD reality changed |

### Pre-review

After **`sql-gym-implement-issue`** opens a draft PR, run **`sql-gym-pre-review`** — it orchestrates independent review, fixes, and handoff. Procedure: [sql-gym-pre-review skill](.cursor/skills/sql-gym-pre-review/SKILL.md). PR template: [.github/pull_request_template.md](.github/pull_request_template.md).

### Prompts

```text
Run write-prd; save under prd/; update prd/README.md active phase when I approve.
```

```text
Plan approved — sql-gym-implement-issue for TIM-42
```

```text
sql-gym-run-phase for Phase 1 — autonomous implementation and GitHub MCP squash merge authorized for implementation PRs and update-prd PRs
```

```text
sql-gym-pre-review for TIM-42 — run the full pre-review loop and mark the PR ready for my review when blocking checks pass
```
