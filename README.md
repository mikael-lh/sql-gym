# sql-gym

A lightweight gym for SQL: practice on curated datasets, run queries, and level up by concept and difficulty.

## Status

Active phase, PRD index, and implementation plans: [prd/README.md](prd/README.md). New product scope requires a PRD update or new phase PRD plus an approved implementation plan.

| | |
|--|--|
| Full workflow reference | [docs/WORKFLOW.md](docs/WORKFLOW.md) |
| Linear project | [sql-gym](https://linear.app/times-api/project/sql-gym-ce6a8985c99e) (`TIM-` issues) |

## Setup

SQL Gym uses Python 3.12, FastAPI, server-rendered templates, and [`uv`](https://docs.astral.sh/uv/) for dependency management. This keeps the scaffold close to the adjacent [`times-api`](https://github.com/mikael-lh/times-api) Python ecosystem while preserving a simple web app path for later SQL practice features.

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

`./scripts/validate-env.sh` wraps the build, lint, static check, and test commands above, then verifies the PRD/workflow files that future agents rely on.

## Phase 0 behavior status

Working behavior:

- FastAPI app startup via `uv run uvicorn app.main:app --reload`.
- Server-rendered home and practice pages.
- `/health` returns a basic status response.
- Static stylesheet serving under `/static/`.
- Pydantic domain models for dataset, exercise, attempt, grading, and progress concepts.
- Tiny Times Archive demo fixture and static demo progress values.
- Baseline validation with `uv build`, ruff, mypy, pytest, and `./scripts/validate-env.sh`.

Placeholder behavior:

- Times demo fixture data is sample-only; it is not the final production Times dataset.
- Dataset, difficulty, timed or untimed mode, SQL editor, grading feedback, and progress controls are visible placeholders.
- SQL is not executed.
- Grading is not implemented.
- Authentication, user accounts, durable progress storage, and AI feedback are not implemented.

## Remaining follow-up decisions

- Production Times refresh process: decide the canonical source, schema refresh workflow, and fixture-to-production data path.
- Grading model: choose exact-result grading rules, partial-credit behavior, and feedback shape.
- Persistence: decide whether progress, attempts, and exercise state need a database or another storage layer.
- Authentication: decide if and when accounts are required for learner progress or personalization.
- AI provider: choose whether AI feedback is in scope, which provider to use, and what rubric constrains it.

## Cursor setup

Install integrations once — see [WORKFLOW § Stack](docs/WORKFLOW.md#stack). Use **repo** skills in [.cursor/skills](.cursor/skills), not same-named marketplace ChatPRD skills. Connect Linear and GitHub in Cursor settings if MCP lookups fail.

## How we work

Specs live in **`prd/`**; work is tracked in **Linear** and shipped via **GitHub PRs** using repo skills. You own product calls, plan sign-off, and merge by default; agents merge only when you explicitly authorize autonomous GitHub MCP merges.

Agent gates: [.cursor/rules/workflow.mdc](.cursor/rules/workflow.mdc). Canonical flow and skill catalog: [docs/WORKFLOW.md § End-to-end flow](docs/WORKFLOW.md#end-to-end-flow).

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

```text
implement-from-prd for prd/phase-0-product-scaffolding.md; produce the plan only and stop for approval.
```

```text
sql-gym-pre-review-reviewer for PR TIM-42 (new agent — review only, no commits)
```

```text
Blocking findings attached — sql-gym-pre-review-fix for TIM-42
```

```text
Reviewer pass clean — sql-gym-pre-review for TIM-42 (final boxes + ready for my review)
```
