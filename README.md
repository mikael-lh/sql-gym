# sql-gym

A lightweight gym for SQL: practice on curated datasets, run queries, and level up by concept and difficulty.

## Status

**Phase 0 scaffold started.** Product vision and an active Phase 0 PRD are in `prd/`; the initial Python/FastAPI development workflow is in place.

| | |
|--|--|
| Full workflow reference | [docs/WORKFLOW.md](docs/WORKFLOW.md) |
| Product specs | [prd/README.md](prd/README.md) |
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

Lint and static checks:

```bash
uv run ruff check .
uv run mypy .
```

Tests:

```bash
uv run pytest
```

Full local validation:

```bash
./scripts/validate-env.sh
```

Phase 0 currently provides the web app foundation only. SQL execution, grading, Times sample fixtures, progress tracking, authentication, and AI feedback are placeholders or future milestones.

## Cursor setup

Install these Cursor marketplace plugins once (details in [WORKFLOW](docs/WORKFLOW.md#tools-and-plugins)):

- **Linear** (MCP) — backlog and issue status
- **Superpowers** — implementation and code review during builds
- **cursor-team-kit** (optional) — `deslop` pass on changed code

Specs, implementation plans, PRD alignment, and PRD updates use repo-local skills in [.cursor/skills](.cursor/skills). Connect Linear in Cursor settings if Linear-backed issue lookup fails.

## How we work

Specs live in **`prd/`** in this repo. Work is tracked in **Linear**, shipped via **GitHub PRs**, and built with **Cursor** using the repo skills in the prompts below. You own product calls, plan sign-off, and merge.

## Workflow

| Step | Your job | In Cursor |
|------|----------|-----------|
| **Requirements** | Approve specs; set the active phase in [prd/README.md](prd/README.md) | local `write-prd` -> commit under `prd/` |
| **Backlog** | Create Linear issues (`TIM-NN`) with a `prd/` link and acceptance criteria | — |
| **Plan** | Review and approve the implementation plan | `sql-gym-start-issue` for `TIM-NN` plus engineering-principles check |
| **Build** | Confirm the plan is approved | `sql-gym-implement-issue` → branch + draft PR |
| **Pre-review** | Wait for the loop to finish; then review the PR yourself | **`sql-gym-pre-review`** for `TIM-NN` (see below) |
| **Ship** | Merge, close the Linear issue; update `prd/` if scope changed | local `update-prd` when useful |

### Pre-review (one command)

After **`sql-gym-implement-issue`** opens a draft PR, run **`sql-gym-pre-review`** in Cursor. That skill **orchestrates the full pass**: independent review (via a readonly subagent or a new chat if needed), fixes on the branch, re-review until there are no blocking findings, then tests/lint, PR checklist, and “ready for your review.”

You do **not** need to invoke `sql-gym-pre-review-reviewer` or `sql-gym-pre-review-fix` yourself unless you choose to split work across separate chats (optional; see [WORKFLOW](docs/WORKFLOW.md#pre-review-before-user-review)).

If pre-review stalls (product decision, plugins unavailable, stuck after several fix rounds), it should leave the PR in draft with checklist boxes unchecked—resolve the blocker and run **`sql-gym-pre-review`** again.

PRs use [.github/pull_request_template.md](.github/pull_request_template.md).

### Prompts

```text
Run write-prd; save under prd/; update prd/README.md active phase when I approve.
```

```text
sql-gym-start-issue for TIM-42
```

```text
Plan approved — sql-gym-implement-issue for TIM-42
```

```text
sql-gym-pre-review for TIM-42 — run the full pre-review loop and mark the PR ready for my review when blocking checks pass
```

## Project rules

- **No product work** until [prd/README.md](prd/README.md) names an active phase and the matching `prd/` doc exists.
- **No application code** until you approve a plan (`sql-gym-start-issue` / local `implement-from-prd`).
- **Your merge review** is still the final gate on product and architecture after pre-review passes.

Deeper process detail, plugin roles, optional split-session pre-review, and engineering standards: [docs/WORKFLOW.md](docs/WORKFLOW.md).
