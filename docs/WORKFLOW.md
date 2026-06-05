# Development workflow

sql-gym uses **ChatPRD + `prd/` + Linear + GitHub**. Product scope lives in **`prd/`**; this document is **how** the **user** and **agents** work together.

**Terms:** **user** = developer; **agent** = Cursor agent (local or cloud).

Hard gates and the PR handoff checklist are **always applied** via [.cursor/rules/workflow.mdc](../.cursor/rules/workflow.mdc). This file is the full playbook.

## Quick reference (agents)

Same as `workflow.mdc` — use when the agent opened this doc mid-task.

**Gates**

- No product work without active phase in [prd/README.md](../prd/README.md) + relevant `prd/` doc.
- Product specs: ChatPRD + `prd/` only (not Superpowers `brainstorming`).
- Application code: approved `implement-from-prd` plan first.
- Stay within the Linear issue / PRD section unless the **user** expands scope.

**Before PR is ready for user review**

- `check-prd-alignment` → note gaps in PR
- Superpowers `code-reviewer` + cursor-team-kit `deslop` (or N/A docs-only)
- Tests/lint, or state CI not configured yet
- PR description: summary, risks, test plan, deviations

Details: [Pre-review before user review](#pre-review-before-user-review).

## Plugins (install in Cursor)

The **user** installs from the [Cursor marketplace](https://cursor.com/marketplace) as needed.

| Step | Plugin | Role |
|------|--------|------|
| 1–2, 5–6 | **ChatPRD** | Product specs, implementation planning, PRD alignment, post-ship updates |
| 3 | **Linear** (MCP / marketplace) | Epics, issues, status—link `prd/`, not full PRD copy |
| 4+ (implementation) | **Superpowers** | TDD, technical plan execution, code review, branch/PR finish |

Do not install overlapping planners (e.g. Compound Engineering or pstack) unless the **user** replaces this stack intentionally.

## Tool roles

| Tool | Owns |
|------|------|
| **ChatPRD** | Authoritative specs; optional cloud copy |
| **`prd/`** (in repo) | Committed specs the user and agents read |
| **Linear** | Backlog, cycles, issue status, priorities |
| **GitHub** | Code, branches, PRs, CI |
| **Superpowers** | Implementation workflows only (not product discovery) |

## End-to-end flow

Each step has an owner and an outcome. Skills named below are from the **ChatPRD** Cursor plugin.

### 1. `write-prd` — decide *what* to build

**Plugin:** ChatPRD only (not Superpowers `brainstorming`).

**When:** Starting the project, a new phase, or a major feature area.

**What happens:** The **user** runs ChatPRD **write-prd** with the **agent** (or directs the agent to run it). Output is requirements—vision, phases, acceptance criteria—saved under `prd/`, starting with `prd/00-product-vision.md` and `prd/phase-N-….md` for the phase being scoped.

**Outcome:** Committed specs in git. [prd/README.md](../prd/README.md) is updated with the **active phase** so agents know implementation is allowed.

---

### 2. `implement-from-prd` — plan *how* to build it

**Plugin:** ChatPRD for the milestone plan; Superpowers **optional** after approval for technical step breakdown (`executing-plans`).

**When:** Before writing application code for a phase or large epic.

**What happens:** The **agent** runs **implement-from-prd** on the relevant `prd/` doc and proposes a **milestone plan**: files to touch, order of work, risks. The **user** reviews and approves (or adjusts) before the **agent** edits code. If helpful, the **agent** may run Superpowers **executing-plans** on the approved plan only—without changing product scope.

**Outcome:** Agreed implementation plan—no surprise architecture or scope creep mid-flight.

---

### 3. Linear — track tasks

**Plugin:** Linear MCP (marketplace).

**When:** After the **user** has an approved plan and wants a prioritized backlog.

**What happens:** The **user** or **agent** creates a **parent epic per phase** and **child issues** from milestones. Each issue links to a `prd/…` section and lists acceptance criteria (see [Linear conventions](#linear-conventions)).

**Outcome:** Traceable work items. Linear holds status; it does **not** replace the PRD.

---

### 4. Code + GitHub PR — ship the change

**Plugins:** Superpowers (TDD, `code-reviewer`, `finishing-a-development-branch` as needed) + `engineering.mdc`.

**When:** Picking up a Linear issue (or an approved task without Linear).

**What happens:** The **agent** branches, implements against acceptance criteria, and opens a PR using [.github/pull_request_template.md](../.github/pull_request_template.md). The **agent** follows [.cursor/rules/engineering.mdc](../.cursor/rules/engineering.mdc) while coding. After a logical chunk, the **agent** runs Superpowers **code-reviewer** against the approved plan.

**Outcome:** Reviewable diff on GitHub, linked to Linear when applicable (`TIM-NN:` in title). The **agent** completes [pre-review](#pre-review-before-user-review) before marking the PR ready for **user** review.

---

### 5. `check-prd-alignment` — verify *what* shipped matches spec

**When:** Part of [pre-review](#pre-review-before-user-review), before the PR is ready for **user** review.

**What happens:** The **agent** runs **check-prd-alignment** against the relevant `prd/phase-*.md` section. It flags missing acceptance criteria, spec drift, and scope gaps. Blocking gaps are **fixed** (or escalated for an approved deviation) as part of the [pre-review iteration loop](#pre-review-before-user-review).

**Outcome:** Confidence the merge matches product intent—not a substitute for code review or tests.

---

### 6. `update-prd` + close Linear — record reality

**When:** After merge (or phase complete).

**What happens:** The **user** or **agent** runs **update-prd** to update ChatPRD / `prd/` if behavior differed from spec. The **user** closes the Linear issue; deferred work goes into PRD **Future work** instead of a silent backlog.

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

## Pre-review before user review

**Agents** (especially cloud) run automated checks **before** the **user** reviews. The **user** judges product and architecture; **agents** handle hygiene and spec alignment.

### Two roles (do not self-review)

| Role | Skill | May commit? |
|------|-------|-------------|
| **Reviewer** | **sql-gym-pre-review-reviewer** | **No** — findings only |
| **Fixer** | **sql-gym-pre-review-fix** | **Yes** — blocking fixes, tests, deslop |

The **implementer** agent must **not** run the judgment review alone. Use a **new agent/chat**, **Cloud Agent handoff**, or a **readonly Task** subagent (`code-reviewer` / `explore`) for the reviewer pass.

**Iterate until pass:** Reviewer → (if blocking) fixer on same branch → reviewer again → … until the reviewer reports **no blocking items**. Then run final tests/lint, check PR boxes, mark ready for **user** review. Non-blocking items may stay as **`Nit:`** per [google-eng-practices.md](references/google-eng-practices.md).

Orchestration: **sql-gym-pre-review** (full loop).

| Step | Tool | Who runs it |
|------|------|-------------|
| Spec alignment | ChatPRD `check-prd-alignment` | **Reviewer** agent |
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
| [.cursor/rules/engineering.mdc](../.cursor/rules/engineering.mdc) | Always-on **agent** guidance: minimal scope, simplicity, DRY, documentation, [Google eng-practices](references/google-eng-practices.md) (adapted) |
| **CI** (add when stack is chosen) | Automated format, lint, and tests on every PR; add as first pre-review checkbox when enabled |
| **User PR review** | Architecture and design judgment (after agent pre-review passes) |

Optional later: enable **Cursor Bugbot** on the repo for automated PR review once there is substantial code—it catches bugs and issues, not product scope.

Do **not** use ChatPRD skills for engineering style; they are for requirements and alignment only.

## Process rules (agents)

Enforced in [.cursor/rules/workflow.mdc](../.cursor/rules/workflow.mdc). Also:

- Do not mark phases complete without updating `prd/`.
- **Implementation:** Superpowers (`executing-plans`, TDD skills, `finishing-a-development-branch`) only after an approved plan from `implement-from-prd`.

## Repo skills (invoke by name)

Thin wrappers around the flow below. Prefer these over “follow WORKFLOW step by step.”

| Skill | When |
|-------|------|
| **sql-gym-start-issue** | Picking up `TIM-NN` — plan only; stops for user approval |
| **sql-gym-implement-issue** | After plan approved — code + draft PR |
| **sql-gym-pre-review-reviewer** | Independent review pass — findings only, no commits |
| **sql-gym-pre-review-fix** | Apply blocking reviewer findings + tests/deslop |
| **sql-gym-pre-review** | Orchestrate reviewer ↔ fixer loop, then ready for user review |

Chain: **start-issue** → (user approves) → **implement-issue** → **pre-review-reviewer** ↔ **pre-review-fix** (until no blocking) → **pre-review** final handoff → (user reviews and merges).

Skills live in [.cursor/skills/](../.cursor/skills/).

## Example prompts (user → agent)

```text
Requirements pass: run write-prd; save under prd/; update prd/README.md active phase when the user approves.
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
Blocking findings attached — sql-gym-pre-review-fix for TIM-42
```

```text
Reviewer pass clean — sql-gym-pre-review for TIM-42 (final boxes + ready for my review)
```

## Secrets

No secrets are committed. When the app is built, document required env vars in `.env.example`. On Cursor Cloud VMs, the **agent** should ask the **user** to add secrets in Cloud settings—do not assume a local `.env` exists.
