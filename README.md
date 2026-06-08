# sql-gym

A lightweight gym for SQL: practice on curated datasets, run queries, and level up by concept and difficulty.

## Status

**Phase 1 active** — dataset and exercise catalog ([prd/phase-1-dataset-exercise-catalog.md](prd/phase-1-dataset-exercise-catalog.md)). Phase 0 scaffold is complete. New product scope requires a PRD update or new phase PRD plus an approved implementation plan.

| | |
|--|--|
| Full workflow reference | [docs/WORKFLOW.md](docs/WORKFLOW.md) |
| Product specs | [prd/README.md](prd/README.md) |
| Phase 1 implementation plan | [docs/phase-1-implementation-plan.md](docs/phase-1-implementation-plan.md) |
| Phase 0 implementation plan | [docs/phase-0-implementation-plan.md](docs/phase-0-implementation-plan.md) |
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

## Phase 1 behavior status

Working behavior:

- Catalog domain models and validation for datasets and exercises.
- Production-ready Times Archive catalog dataset with 50 structured exercise entries.
- `/practice` catalog browsing with dataset, difficulty, and mode filters.
- `/practice/{dataset_id}/{exercise_id}` exercise preview pages linked from the practice flow.
- User-friendly 404 responses for unknown exercise preview routes.
- Inline empty states when practice filters return no exercises.
- Hints and sample SQL disclosure patterns that keep illustrative SQL hidden by default.

Placeholder behavior:

- SQL is not executed.
- Grading is not implemented.
- Authentication, user accounts, durable progress storage, and AI feedback are not implemented.
- Timed-mode scoring behavior is not active even when exercises are labeled Timed.
- Article row data still uses the small schema-aligned demo fixture while catalog exercises are production-ready metadata.

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

- Production Times refresh process: decide the canonical source, schema refresh workflow, and fixture-to-production data path.
- Grading model: choose exact-result grading rules, partial-credit behavior, and feedback shape.
- Persistence: decide whether progress, attempts, and exercise state need a database or another storage layer.
- Authentication: decide if and when accounts are required for learner progress or personalization.
- AI provider: choose whether AI feedback is in scope, which provider to use, and what rubric constrains it.

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
