# Development workflow

sql-gym uses **ChatPRD + `prd/` + Linear + GitHub**. Product scope lives in **`prd/`**; this document is **how** the **human** (solo developer) and **agents** work together.

**Terms:** **human** = solo developer; **agent** = Cursor agent (local or cloud).

Hard gates and the PR handoff checklist are **always applied** via [.cursor/rules/workflow.mdc](../.cursor/rules/workflow.mdc). This file is the full playbook.

## Quick reference (agents)

Same as `workflow.mdc` — use when the agent opened this doc mid-task.

**Gates**

- No product work without active phase in [prd/README.md](../prd/README.md) + relevant `prd/` doc.
- Product specs: ChatPRD + `prd/` only (not Superpowers `brainstorming`).
- Application code: approved `implement-from-prd` plan first.
- Stay within the Linear issue / PRD section unless the **human** expands scope.

**Before PR is ready for human review**

- `check-prd-alignment` → note gaps in PR
- Superpowers `code-reviewer` + cursor-team-kit `deslop` (or N/A docs-only)
- Tests/lint, or state CI not configured yet
- PR description: summary, risks, test plan, deviations

Details: [Pre-review before human review](#pre-review-before-human-review).

## Plugins (install in Cursor)

The **human** installs from the [Cursor marketplace](https://cursor.com/marketplace) as needed.

| Step | Plugin | Role |
|------|--------|------|
| 1–2, 5–6 | **ChatPRD** | Product specs, implementation planning, PRD alignment, post-ship updates |
| 3 | **Linear** (MCP / marketplace) | Epics, issues, status—link `prd/`, not full PRD copy |
| 4+ (implementation) | **Superpowers** | TDD, technical plan execution, code review, branch/PR finish |

Do not install overlapping planners (e.g. Compound Engineering or pstack) unless the **human** replaces this stack intentionally.

## Tool roles

| Tool | Owns |
|------|------|
| **ChatPRD** | Authoritative specs; optional cloud copy |
| **`prd/`** (in repo) | Committed specs the human and agents read |
| **Linear** | Backlog, cycles, issue status, priorities |
| **GitHub** | Code, branches, PRs, CI |
| **Superpowers** | Implementation workflows only (not product discovery) |

## End-to-end flow

Each step has an owner and an outcome. Skills named below are from the **ChatPRD** Cursor plugin.

### 1. `write-prd` — decide *what* to build

**Plugin:** ChatPRD only (not Superpowers `brainstorming`).

**When:** Starting the project, a new phase, or a major feature area.

**What happens:** The **human** runs ChatPRD **write-prd** with the **agent** (or directs the agent to run it). Output is requirements—vision, phases, acceptance criteria—saved under `prd/`, starting with `prd/00-product-vision.md` and `prd/phase-N-….md` for the phase being scoped.

**Outcome:** Committed specs in git. [prd/README.md](../prd/README.md) is updated with the **active phase** so agents know implementation is allowed.

---

### 2. `implement-from-prd` — plan *how* to build it

**Plugin:** ChatPRD for the milestone plan; Superpowers **optional** after approval for technical step breakdown (`executing-plans`).

**When:** Before writing application code for a phase or large epic.

**What happens:** The **agent** runs **implement-from-prd** on the relevant `prd/` doc and proposes a **milestone plan**: files to touch, order of work, risks. The **human** reviews and approves (or adjusts) before the **agent** edits code. If helpful, the **agent** may run Superpowers **executing-plans** on the approved plan only—without changing product scope.

**Outcome:** Agreed implementation plan—no surprise architecture or scope creep mid-flight.

---

### 3. Linear — track tasks

**Plugin:** Linear MCP (marketplace).

**When:** After the **human** has an approved plan and wants a prioritized backlog.

**What happens:** The **human** or **agent** creates a **parent epic per phase** and **child issues** from milestones. Each issue links to a `prd/…` section and lists acceptance criteria (see [Linear conventions](#linear-conventions)).

**Outcome:** Traceable work items. Linear holds status; it does **not** replace the PRD.

---

### 4. Code + GitHub PR — ship the change

**Plugins:** Superpowers (TDD, `code-reviewer`, `finishing-a-development-branch` as needed) + `engineering.mdc`.

**When:** Picking up a Linear issue (or an approved task without Linear).

**What happens:** The **agent** branches, implements against acceptance criteria, and opens a PR using [.github/pull_request_template.md](../.github/pull_request_template.md). The **agent** follows [.cursor/rules/engineering.mdc](../.cursor/rules/engineering.mdc) while coding. After a logical chunk, the **agent** runs Superpowers **code-reviewer** against the approved plan.

**Outcome:** Reviewable diff on GitHub, linked to Linear when applicable (`TIM-NN:` in title). The **agent** completes [pre-review](#pre-review-before-human-review) before marking the PR ready for **human** review.

---

### 5. `check-prd-alignment` — verify *what* shipped matches spec

**When:** Part of [pre-review](#pre-review-before-human-review), before the PR is ready for **human** review.

**What happens:** The **agent** runs **check-prd-alignment** against the relevant `prd/phase-*.md` section. It flags missing acceptance criteria, spec drift, and scope gaps. The **agent** records the result in the PR description.

**Outcome:** Confidence the merge matches product intent—not a substitute for code review or tests.

---

### 6. `update-prd` + close Linear — record reality

**When:** After merge (or phase complete).

**What happens:** The **human** or **agent** runs **update-prd** to update ChatPRD / `prd/` if behavior differed from spec. The **human** closes the Linear issue; deferred work goes into PRD **Future work** instead of a silent backlog.

**Outcome:** Specs and tickets match what is actually in `main`.

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

## Pre-review before human review

**Agents** (especially cloud) run automated checks **before** the **human** reviews. The **human** judges product and architecture; **agents** handle hygiene and spec alignment.

| Step | Tool | Who runs it |
|------|------|-------------|
| Spec alignment | ChatPRD `check-prd-alignment` | **Agent** — note gaps in PR |
| Code vs plan | Superpowers `code-reviewer` | **Agent** — vs approved `implement-from-prd` plan |
| Slop / style pass | cursor-team-kit `deslop` | **Agent** — on changed code; skip for docs-only PRs |
| Verification | tests / lint | **Agent** — when [CI](#engineering-standards-code-quality) exists, must be green first |

**PR description must include:** summary, risks, test plan (or “CI not configured — ran …”), alignment notes, PRD deviations.

The **human** installs plugins: `/add-plugin superpowers`, `/add-plugin cursor-team-kit`.

---

## GitHub conventions

- **Default branch:** `main`
- **PRs:** use [.github/pull_request_template.md](../.github/pull_request_template.md) (includes agent pre-review checklist)
- **Done:** merged PR + Linear issue closed + PRD updated if scope changed

## ChatPRD plugin

Product/requirements only—not code style.

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

**Not used here:** `brainstorming` (use ChatPRD `write-prd` for product work).

## Engineering standards (code quality)

| Mechanism | Role |
|-----------|------|
| [.cursor/rules/engineering.mdc](../.cursor/rules/engineering.mdc) | Always-on **agent** guidance: minimal scope, simplicity, DRY, documentation, match conventions |
| **CI** (add when stack is chosen) | Automated format, lint, and tests on every PR; add as first pre-review checkbox when enabled |
| **Human PR review** | Architecture and design judgment (after agent pre-review passes) |

Optional later: enable **Cursor Bugbot** on the repo for automated PR review once there is substantial code—it catches bugs and issues, not product scope.

Do **not** use ChatPRD skills for engineering style; they are for requirements and alignment only.

## Process rules (agents)

Enforced in [.cursor/rules/workflow.mdc](../.cursor/rules/workflow.mdc). Also:

- Do not mark phases complete without updating `prd/`.
- **Implementation:** Superpowers (`executing-plans`, TDD skills, `finishing-a-development-branch`) only after an approved plan from `implement-from-prd`.

## Example prompts (human → agent)

```text
Requirements pass: run write-prd; save under prd/; update prd/README.md active phase when the human approves.
```

```text
Working on Linear TIM-42. Read prd/phase-1-….md § "Run SQL". Propose a plan (implement-from-prd) before editing files.
```

```text
PR ready for TIM-42: complete pre-review (check-prd-alignment, code-reviewer, deslop, tests); then mark ready for human review.
```

## Secrets

No secrets are committed. When the app is built, document required env vars in `.env.example`. On Cursor Cloud VMs, the **agent** should ask the **human** to add secrets in Cloud settings—do not assume a local `.env` exists.
