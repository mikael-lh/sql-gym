# Development workflow

sql-gym uses **repo skills + `prd/` + Linear + GitHub**. Product scope lives in **`prd/`**; this document is **how** the **user** and **agents** work together.

**Terms:** **user** = developer; **agent** = Cursor agent (local or cloud).

**Gates:** [.cursor/rules/workflow.mdc](../.cursor/rules/workflow.mdc) (always applied). This doc expands on that playbook; it does not restate the gates.

Human quick start: [README.md § How we work](../README.md#how-we-work).

## Stack

| Layer | What | Install / auth |
|-------|------|----------------|
| **Specs** | `prd/` directory | Committed in repo — authoritative product and phase requirements |
| **Repo skills** | [.cursor/skills/](../.cursor/skills/) | Committed — invoke by skill name (see [Skills catalog](#skills-catalog)) |
| **Backlog** | [Linear MCP](https://linear.app/times-api/project/sql-gym-ce6a8985c99e) | **User:** Cursor marketplace + MCP auth in settings |
| **Delivery** | **GitHub MCP** | PRs, comments, CI status; **authorized** merges via `merge_pull_request` (not `gh` writes on cloud agents) |
| **Implementation** | [Superpowers](https://cursor.com/marketplace) plugin | **User:** marketplace — plan execution, TDD, code review, branch/PR finish |
| **Style pass** | cursor-team-kit `deslop` | **User:** optional marketplace plugin |

Repo skills own product specs, planning, alignment, and sql-gym delivery orchestration. Superpowers owns implementation mechanics only — not product discovery.

Do not install overlapping planners (e.g. Compound Engineering or pstack) unless the **user** replaces this stack intentionally.

## End-to-end flow

Canonical chain:

```text
write-prd
  -> user approves and merges PRD
  -> implement-from-prd
  -> user approves and merges plan + Linear issues are created
  -> sql-gym-implement-issue
  -> sql-gym-pre-review
       -> pre-review-reviewer <-> pre-review-fix until no blocking findings
       -> pre-review final handoff
  -> user reviews and merges, or autonomous phase runner merges when explicitly authorized for implementation PRs
  -> update-prd
  -> user approves and merges PRD reality update, or autonomous phase runner merges when explicitly authorized for update-prd PRs
```

Each step has an owner and an outcome. Skills named below are repo skills in [.cursor/skills/](../.cursor/skills/).

| Step | Owner | What happens | Outcome |
|------|-------|--------------|---------|
| `write-prd` | User + agent | Define or revise product/phase requirements under `prd/`. Do not use Superpowers `brainstorming` for product scope. | PRD PR merged; `prd/README.md` names the active phase only after user approval. |
| `implement-from-prd` | User + agent | Produce the phase milestone plan, check it against engineering guidance, and stop for approval. | Approved implementation plan PR merged. |
| Linear backlog | User or agent | Create a parent issue and child `TIM-NN` issues from the approved plan. Each issue links `prd/…` and concise acceptance criteria. | Traceable issue list; Linear tracks status but does not replace `prd/`. |
| `sql-gym-implement-issue` | Agent | For one `TIM-NN`, verify Linear + PRD + approved plan alignment, branch, implement, test, and open a PR. | Focused implementation PR with pre-review boxes unchecked. |
| `sql-gym-pre-review` | Agent + independent reviewer | Orchestrate `pre-review-reviewer` ↔ `pre-review-fix` until there are no blocking findings, then run final verification and update PR boxes. | PR ready for user review or autonomous merge if explicitly authorized. |
| Merge | User, or autonomous runner when explicitly authorized for implementation PRs | Merge the implementation PR. Autonomous agents use GitHub MCP `merge_pull_request`; do not use `gh` for writes. | Shipped change on `main`. |
| `update-prd` | Agent | Record what actually shipped, deviations, deferred scope, and completed requirements when PRD reality changed. | PRD reality update PR. |
| PRD reality merge | User, or autonomous runner when explicitly authorized for update-prd PRs | Merge the `update-prd` PR, close/update Linear, pull `main`, continue if running a phase. | Specs and tickets match `main`. |

For approved phase plans that should run without per-ticket prompts, use **`sql-gym-run-phase`**.

Phases and detailed scope live in [prd/00-product-vision.md](../prd/00-product-vision.md) and [prd/README.md](../prd/README.md).

## Skills catalog

Prefer invoking these skills by name over following this doc step by step. All live in [.cursor/skills/](../.cursor/skills/).

| Phase | Skill | When / outcome |
|-------|-------|----------------|
| Spec | **write-prd** | Write or revise a product, phase, or feature PRD under `prd/` |
| Plan | **implement-from-prd** | Plan implementation from a local PRD; stops for user approval |
| Align | **check-prd-alignment** | Compare a branch or PR diff against a linked `prd/` section (pre-review) |
| Build | **sql-gym-implement-issue** | After plan approval — one `TIM-NN`: verify PRD/plan, implement, open draft PR |
| Build | **sql-gym-run-phase** | Autonomously run approved phase child issues in sequence |
| Review | **sql-gym-pre-review** | Orchestrate reviewer ↔ fixer loop, then ready for user review |
| Review | **sql-gym-pre-review-reviewer** | Independent review pass — findings only, no commits |
| Review | **sql-gym-pre-review-fix** | Apply blocking reviewer findings, tests, deslop |
| Reality | **update-prd** | Record what shipped, deviations, and deferred work in `prd/` |

### Superpowers plugin (marketplace)

Implementation only — do not use for product scope. Use after an approved plan from **implement-from-prd**.

| Intent | Skill |
|--------|--------|
| Execute an approved technical plan | `executing-plans` |
| Test-driven implementation | TDD skills (when stack has tests) |
| Review code vs plan and standards | `code-reviewer` |
| Merge / PR / branch cleanup | `finishing-a-development-branch` |

**Not used here:** `brainstorming` (use **write-prd** for product work).

The **user** installs marketplace plugins: `/add-plugin superpowers`, `/add-plugin cursor-team-kit` (optional).

## Pre-review before user review

Run [**sql-gym-pre-review**](../.cursor/skills/sql-gym-pre-review/SKILL.md) before **user** review or authorized autonomous merge — it orchestrates independent review, fixes, and handoff. Optional split-session skills: [reviewer](../.cursor/skills/sql-gym-pre-review-reviewer/SKILL.md), [fix](../.cursor/skills/sql-gym-pre-review-fix/SKILL.md). Gates: [.cursor/rules/workflow.mdc](../.cursor/rules/workflow.mdc#workflow-gates). PR checkboxes: [.github/pull_request_template.md](../.github/pull_request_template.md).

## Linear conventions

- **Project:** [sql-gym](https://linear.app/times-api/project/sql-gym-ce6a8985c99e) (separate from the Times API product backlog; issues use prefix `TIM-`)
- **Epic:** one parent issue per phase (e.g. `Phase 1 | Dataset and exercise catalog`)
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
- **Branch naming:** `cursor/<short-desc>-<suffix>` — the cloud agent template supplies the suffix for the active session (e.g. `cursor/tim-42-parser-7a6a`). Do not use `feature/…` or other conventions.
- **PRs:** use [.github/pull_request_template.md](../.github/pull_request_template.md) (includes agent pre-review checklist)
- **Merges:** user merges by default; autonomous agents merge only when explicitly authorized for that run and PR type, via GitHub MCP (not `gh` writes)
- **Done:** merged PR + Linear issue closed + PRD updated if scope changed

## Engineering standards

Always-on agent guidance: [.cursor/rules/engineering.mdc](../.cursor/rules/engineering.mdc) and [google-eng-practices.md](references/google-eng-practices.md).

- **CI** (add when stack is chosen): automated format, lint, and tests on every PR; add as first pre-review checkbox when enabled
- **User PR review:** architecture and design judgment after agent pre-review passes

Optional later: enable **Cursor Bugbot** on the repo for automated PR review once there is substantial code — it catches bugs and issues, not product scope.

Do **not** use repo PRD skills for engineering style; they are for requirements and alignment only.

## Example prompts (agent-oriented)

Common user prompts live in [README.md § Prompts](../README.md#prompts). Use these when splitting work across sessions or authorizing autonomous runs:

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

## Secrets

See [.cursor/rules/workflow.mdc § Agent references](../.cursor/rules/workflow.mdc#agent-references).
