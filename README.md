# sql-gym

A lightweight gym for SQL: practice on curated datasets, run queries, and level up by concept and difficulty.

## Status

**Early setup.** Process and agent workflow are documented; product requirements and application code are not started yet.

- Workflow (full playbook): [docs/WORKFLOW.md](docs/WORKFLOW.md)
- Product specs: [prd/README.md](prd/README.md) (requirements gathering pending)

## Working with this repo (humans)

Use **Cursor agents** for implementation and review; you own product decisions, plan approval, and merge. Specs live in **`prd/`**; tasks in **Linear** (`TIM-` prefix, [sql-gym project](https://linear.app/times-api/project/sql-gym-ce6a8985c99e)); code in **GitHub PRs**.

### One-time setup

1. Install Cursor plugins (see [WORKFLOW — Plugins](docs/WORKFLOW.md#plugins-install-in-cursor)): **ChatPRD**, **Linear** (MCP), **Superpowers**. Optional: **cursor-team-kit** (`deslop`) on desktop.
2. Connect ChatPRD and Linear MCP in Cursor settings if prompts fail in cloud agents.

### Typical flow

| Step | You do | Agent skill / ChatPRD |
|------|--------|------------------------|
| 1. Requirements | Approve specs and active phase in [prd/README.md](prd/README.md) | ChatPRD `write-prd` → files under `prd/` |
| 2. Backlog | Create or refine Linear issues (`TIM-NN`) linking a `prd/` section + acceptance criteria | — |
| 3. Plan | Review and **approve** the implementation plan | **`sql-gym-start-issue`** for `TIM-NN` (plan only; agent stops) |
| 4. Build | Confirm plan approved | **`sql-gym-implement-issue`** → branch + **draft PR** (template in [.github/pull_request_template.md](.github/pull_request_template.md)) |
| 5. Agent pre-review | Start a **new agent/chat** for review (not the implementer session) | **`sql-gym-pre-review-reviewer`** → findings on the PR, no commits |
| 6. Fixes | If blocking items exist | **`sql-gym-pre-review-fix`** on the PR branch → push → go back to step 5 |
| 7. Handoff | When reviewer reports no blocking items | **`sql-gym-pre-review`** → check PR boxes, mark ready for **your** review |
| 8. Ship | Review PR, merge, close Linear issue; update `prd/` if scope changed | ChatPRD `update-prd` when appropriate |

Agents **iterate** until pre-review passes—they should not check boxes or ask you to review while blocking findings remain. You still do final review (architecture, product judgment).

### Prompts to copy

```text
Requirements: run write-prd; save under prd/; update prd/README.md active phase when I approve.
```

```text
sql-gym-start-issue for TIM-42
```

```text
Plan approved — sql-gym-implement-issue for TIM-42
```

```text
sql-gym-pre-review-reviewer for PR TIM-42 (new agent — review only, no commits)
```

```text
Blocking findings on the PR — sql-gym-pre-review-fix for TIM-42
```

```text
Reviewer pass clean — sql-gym-pre-review for TIM-42 (final boxes + ready for my review)
```

### Gates (do not skip)

- No product features until [prd/README.md](prd/README.md) names an **active phase** and the relevant `prd/` doc exists.
- No application code until you approve a plan from `implement-from-prd` / **sql-gym-start-issue**.
- Pre-review: **reviewer** and **implementer** must not be the same blind self-review—use a new chat or a readonly review subagent.

More detail: [docs/WORKFLOW.md](docs/WORKFLOW.md) · Repo skills: [.cursor/skills/](.cursor/skills/)
