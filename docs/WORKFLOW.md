# Development workflow

sql-gym uses **ChatPRD + `prd/` + Linear + GitHub**. Product scope, phases, and acceptance criteria live in **`prd/`** only—this document covers **process** (how we work).

Cursor loads this via [.cursor/rules/workflow.mdc](../.cursor/rules/workflow.mdc).

## Tool roles

| Tool | Owns |
|------|------|
| **ChatPRD** | Authoritative specs; optional cloud copy |
| **`prd/`** (in repo) | Committed specs agents and humans read |
| **Linear** | Backlog, cycles, issue status, priorities |
| **GitHub** | Code, branches, PRs, CI |

Do not duplicate full PRD text in Linear issues—link `prd/…` and list acceptance criteria.

## End-to-end flow

```text
1. write-prd
   → ChatPRD + prd/00-product-vision.md
   → prd/phase-N-….md for the active phase only

2. implement-from-prd
   → Milestone plan (files, order, risks) → user approves

3. Linear
   → Parent epic per phase; child issues from milestones
   → Labels: phase-N, area:*, type:feature|spike|chore

4. Code + GitHub PR
   → Branch: cursor/<desc>-0eb3 or feature/GYM-NN-<desc>
   → PR title: GYM-NN: <summary>

5. check-prd-alignment (before merge)

6. update-prd + close Linear issues; deferrals → PRD "Future work"
```

Phases and scope are defined in [prd/00-product-vision.md](../prd/00-product-vision.md) and indexed in [prd/README.md](../prd/README.md)—not in this file.

## Linear conventions

- **Project:** sql-gym (or your team’s equivalent)
- **Epic:** one parent issue per phase (e.g. `Phase 0 – Data & grading`)
- **Issue title:** `Phase N | Short title`
- **Issue body template:**

  ```markdown
  **PRD:** prd/phase-N-….md § "<section>"
  **Acceptance criteria**
  - [ ] …
  **Out of scope**
  - …
  ```

## GitHub conventions

- **Default branch:** `main`
- **PRs:** use [.github/pull_request_template.md](../.github/pull_request_template.md)
- **Done:** merged PR + Linear issue closed + PRD updated if scope changed

## Agent session prompts (examples)

```text
Requirements pass: help draft prd/00-product-vision.md; ask clarifying questions first.
```

```text
Working on Linear GYM-42. Read prd/phase-1-….md § "Run SQL". Follow docs/WORKFLOW.md.
Propose a plan before editing files.
```

```text
PR ready for GYM-42: run tests, check-prd-alignment against prd/phase-1-….md.
```

## ChatPRD plugin

Enable the ChatPRD Cursor plugin for this repo.

| Intent | Skill |
|--------|--------|
| Write or expand specs | `write-prd` (save under `prd/`) |
| Plan implementation from a PRD | `implement-from-prd` |
| Pre-merge requirement check | `check-prd-alignment` |
| Record what shipped vs spec | `update-prd` |

## Process rules (agents)

- Do not invent product requirements or mark phases complete without PRD updates.
- Do not expand scope beyond the active Linear issue / PRD section without user approval.
- Document PRD deviations in the PR description, not only in chat.

## Secrets

No secrets are committed. When the app is built, document required env vars in `.env.example`. On Cursor Cloud VMs, ask the user to add secrets in Cloud settings—do not assume a local `.env` exists.
