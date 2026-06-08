# Development workflow

sql-gym uses **repo-local PRD skills + `prd/` + Linear + GitHub**. Product scope lives in **`prd/`**; this document is **how** the **user** and **agents** work together.

**Terms:** **user** = developer; **agent** = Cursor agent (local or cloud).

Hard gates and the PR handoff checklist are **always applied** via [.cursor/rules/workflow.mdc](../.cursor/rules/workflow.mdc). This file is the full playbook.

## Quick reference (agents)

Same as `workflow.mdc` — use when the agent opened this doc mid-task.

**Gates**

- No product work without active phase in [prd/README.md](../prd/README.md) + relevant `prd/` doc.
- Product specs: repo-local PRD skills + `prd/` only (not Superpowers `brainstorming`).
- Application code: approved local `implement-from-prd` plan first.
- Stay within the Linear issue / PRD section unless the **user** expands scope.

**Before PR is ready for user review**

- local `check-prd-alignment` -> note gaps in PR
- Superpowers `code-reviewer` + cursor-team-kit `deslop` (or N/A docs-only)
- Tests/lint, or state CI not configured yet
- PR description: summary, risks, test plan, deviations

Details: [Pre-review before user review](#pre-review-before-user-review).

## Tools and plugins

The **user** installs marketplace plugins from the [Cursor marketplace](https://cursor.com/marketplace) as needed. Repo-local skills are committed under `.cursor/skills/` and do not require marketplace installation.

| Step | Tool | Role |
|------|------|------|
| 1–2, 5–6 | **Repo-local PRD skills** | Product specs, implementation planning, PRD alignment, post-ship updates |
| 3 | **Linear** (MCP / marketplace) | Epics, issues, status—link `prd/`, not full PRD copy |
| 4+ (implementation) | **Superpowers** | TDD, technical plan execution, code review, branch/PR finish |

Do not install overlapping planners (e.g. Compound Engineering or pstack) unless the **user** replaces this stack intentionally.

## Tool roles

| Tool | Owns |
|------|------|
| **Repo-local PRD skills** | Deterministic PRD workflows that read and write `prd/` |
| **`prd/`** (in repo) | Authoritative committed specs the user and agents read |
| **Linear** | Backlog, cycles, issue status, priorities |
| **GitHub** | Code, branches, PRs, CI |
| **Superpowers** | Implementation workflows only (not product discovery) |

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

Each step has an owner and an outcome. Skills named below are repo-local skills in [.cursor/skills/](../.cursor/skills/).

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

---

Phases and detailed scope live in [prd/00-product-vision.md](../prd/00-product-vision.md) and [prd/README.md](../prd/README.md).

## Linear conventions

- **Project:** [sql-gym](https://linear.app/times-api/project/sql-gym-ce6a8985c99e) (separate from the Times API product backlog; issues use prefix `TIM-`)
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

## Pre-review before user review

**Agents** (especially cloud) run automated checks **before** the **user** reviews or before an explicitly authorized autonomous merge. The **user** owns product and architecture judgment through PRD/plan approval; **agents** handle hygiene and spec alignment.

### Two roles (do not self-review)

| Role | Skill | May commit? |
|------|-------|-------------|
| **Reviewer** | **sql-gym-pre-review-reviewer** | **No** — findings only |
| **Fixer** | **sql-gym-pre-review-fix** | **Yes** — blocking fixes, tests, deslop |

The **implementer** agent must **not** run the judgment review alone. Use a **new agent/chat**, **Cloud Agent handoff**, or a **readonly Task** subagent (`code-reviewer` / `explore`) for the reviewer pass.

**Iterate until pass:** Reviewer → (if blocking) fixer on same branch → reviewer again → … until the reviewer reports **no blocking items**. Then run final tests/lint, check PR boxes, and mark ready for **user** review or authorized autonomous merge. Non-blocking items may stay as **`Nit:`** per [google-eng-practices.md](references/google-eng-practices.md).

Orchestration: **sql-gym-pre-review** (full loop).

| Step | Tool | Who runs it |
|------|------|-------------|
| Spec alignment | local `check-prd-alignment` | **Reviewer** agent |
| Code vs plan | Superpowers `code-reviewer` | **Reviewer** agent |
| Code review | [google-eng-practices.md](references/google-eng-practices.md) checklist | **Reviewer** agent; `Nit:` for optional |
| Apply fixes | Branch edits | **Fixer** agent |
| Slop / style pass | cursor-team-kit `deslop` | **Fixer** agent (or N/A docs-only) |
| Verification | tests / lint | **Fixer** agent — must be green before re-review |

Post each reviewer pass under **`## Pre-review findings (pass N)`** on the PR.

**PR description must include:** summary, risks, test plan (or “CI not configured — ran …”), alignment notes, PRD deviations, and any remaining **`Nit:`** items.

**Escalate** to the **user** (leave boxes unchecked, keep draft) when a product/architecture call is needed, independent review is not possible, plugins cannot run, or agents are stuck after several cycles.

The **user** installs plugins: `/add-plugin superpowers`, `/add-plugin cursor-team-kit`.

---

## GitHub conventions

- **Default branch:** `main`
- **Branch naming:** `cursor/<short-desc>-<suffix>` — the cloud agent template supplies the suffix for the active session (e.g. `cursor/tim-42-parser-7a6a`). Do not use `feature/…` or other conventions.
- **PRs:** use [.github/pull_request_template.md](../.github/pull_request_template.md) (includes agent pre-review checklist)
- **Done:** merged PR + Linear issue closed + PRD updated if scope changed

## Repo-local PRD skills

Product/requirements only--not code style. These skills live in [.cursor/skills/](../.cursor/skills/) and do not require ChatPRD cloud access.

| Intent | Skill |
|--------|--------|
| Write or expand specs | `write-prd` (save under `prd/`) |
| Plan implementation from a PRD | `implement-from-prd` |
| Pre-merge requirement check | `check-prd-alignment` |
| Record what shipped vs spec | `update-prd` |

## Superpowers plugin

Implementation only—do not use for product scope (see [Process rules](#process-rules-agents)).

| Intent | Skill |
|--------|--------|
| Execute an approved technical plan | `executing-plans` |
| Test-driven implementation | TDD skills (when stack has tests) |
| Review code vs plan and standards | `code-reviewer` |
| Merge / PR / branch cleanup | `finishing-a-development-branch` |

**Not used here:** `brainstorming` (use local `write-prd` for product work).

## Engineering standards (code quality)

| Mechanism | Role |
|-----------|------|
| [.cursor/rules/engineering.mdc](../.cursor/rules/engineering.mdc) | Always-on **agent** guidance: minimal scope, simplicity, DRY, documentation, [Google eng-practices](references/google-eng-practices.md) (adapted) |
| **CI** (add when stack is chosen) | Automated format, lint, and tests on every PR; add as first pre-review checkbox when enabled |
| **User PR review** | Architecture and design judgment (after agent pre-review passes) |

Optional later: enable **Cursor Bugbot** on the repo for automated PR review once there is substantial code—it catches bugs and issues, not product scope.

Do **not** use PRD skills for engineering style; they are for requirements and alignment only.

## Process rules (agents)

Enforced in [.cursor/rules/workflow.mdc](../.cursor/rules/workflow.mdc). Also:

- Do not mark phases complete without updating `prd/`.
- **Implementation:** Superpowers (`executing-plans`, TDD skills, `finishing-a-development-branch`) only after an approved plan from local `implement-from-prd`.

## Repo skills (invoke by name)

Thin wrappers around the flow below. Prefer these over “follow WORKFLOW step by step.”

| Skill | When |
|-------|------|
| **write-prd** | Write or revise a local product, phase, or feature PRD |
| **implement-from-prd** | Plan implementation from a local PRD; stops for approval |
| **check-prd-alignment** | Compare a branch or PR diff against a local PRD |
| **update-prd** | Record what shipped, deviations, and future work in `prd/` |
| **sql-gym-implement-issue** | After phase plan approval — verify one `TIM-NN` against PRD/plan, code, and open draft PR |
| **sql-gym-run-phase** | Autonomously run approved phase child issues in sequence |
| **sql-gym-pre-review-reviewer** | Independent review pass — findings only, no commits |
| **sql-gym-pre-review-fix** | Apply blocking reviewer findings + tests/deslop |
| **sql-gym-pre-review** | Orchestrate reviewer ↔ fixer loop, then ready for user review |

Chain: **write-prd** → (user approves and merges) → **implement-from-prd** → (user approves and merges + Linear issues exist) → **sql-gym-implement-issue** → **sql-gym-pre-review** (`pre-review-reviewer` ↔ `pre-review-fix` until no blocking) → merge → **update-prd** → merge.

Skills live in [.cursor/skills/](../.cursor/skills/).

## Example prompts (user → agent)

```text
Requirements pass: run write-prd; save under prd/; update prd/README.md active phase when the user approves.
```

```text
implement-from-prd for prd/phase-0-product-scaffolding.md; produce the plan only and stop for approval.
```

```text
Plan approved — sql-gym-implement-issue for TIM-42
```

```text
sql-gym-run-phase for Phase 1 — autonomous implementation and GitHub MCP squash merge authorized for implementation PRs and update-prd PRs
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

No secrets are committed. When the app is built, document required env vars in `.env.example`. On Cursor Cloud VMs, the **agent** should ask the **user** to add secrets in Cloud settings—do not assume a local `.env` exists.
