# sql-gym

A lightweight gym for SQL: practice on curated datasets, run queries, and level up by concept and difficulty.

## Status

**Early setup.** The development workflow is documented below; product requirements and application code are not started yet.

| | |
|--|--|
| Full workflow reference | [docs/WORKFLOW.md](docs/WORKFLOW.md) |
| Product specs | [prd/README.md](prd/README.md) |
| Linear project | [sql-gym](https://linear.app/times-api/project/sql-gym-ce6a8985c99e) (`TIM-` issues) |

## Setup

Install these Cursor marketplace plugins once (details in [WORKFLOW](docs/WORKFLOW.md#plugins-install-in-cursor)):

- **ChatPRD** — specs, implementation plans, PRD alignment
- **Linear** (MCP) — backlog and issue status
- **Superpowers** — implementation and code review during builds
- **cursor-team-kit** (optional) — `deslop` pass on changed code

Connect ChatPRD and Linear in Cursor settings if skills fail to run (common in Cloud sessions).

## How we work

Specs live in **`prd/`** in this repo. Work is tracked in **Linear**, shipped via **GitHub PRs**, and built with **Cursor** using the repo skills named in the prompts below. You own product calls, plan sign-off, and merge.

## Workflow

| Step | Your job | In Cursor |
|------|----------|-----------|
| **Requirements** | Approve specs; set the active phase in [prd/README.md](prd/README.md) | `write-prd` → commit under `prd/` |
| **Backlog** | Create Linear issues (`TIM-NN`) with a `prd/` link and acceptance criteria | — |
| **Plan** | Review and approve the implementation plan | `sql-gym-start-issue` for `TIM-NN` |
| **Build** | Confirm the plan is approved | `sql-gym-implement-issue` → branch + draft PR |
| **Review** | Open a **new Cursor chat** for review (not the same session that built the PR) | `sql-gym-pre-review-reviewer` |
| **Fix** | If the review lists blocking items | `sql-gym-pre-review-fix`, then run review again |
| **Ready for you** | When review reports no blocking items | `sql-gym-pre-review` → PR checklist complete |
| **Ship** | Review the PR, merge, close the Linear issue; update `prd/` if scope changed | `update-prd` when useful |

Pre-review **loops** until blocking findings are resolved—don’t review a PR that still has open blocking items on the checklist. Your merge review is still the final call on product and architecture.

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
sql-gym-pre-review-reviewer for PR TIM-42 — review only, no commits
```

```text
Blocking findings on the PR — sql-gym-pre-review-fix for TIM-42
```

```text
Reviewer pass clean — sql-gym-pre-review for TIM-42 — ready for my review
```

## Project rules

- **No product work** until [prd/README.md](prd/README.md) names an active phase and the matching `prd/` doc exists.
- **No application code** until you approve a plan (`sql-gym-start-issue` / `implement-from-prd`).
- **Independent review** — use a fresh Cursor chat for `sql-gym-pre-review-reviewer`; don’t use the same session that implemented the PR for the judgment pass.

Deeper process detail, plugin roles, and engineering standards: [docs/WORKFLOW.md](docs/WORKFLOW.md).
