# Development workflow

sql-gym uses **ChatPRD + `prd/` + Linear + GitHub**. Product scope lives in **`prd/`**; this document is **how** the team and agents work.

Cursor applies [.cursor/rules/workflow.mdc](../.cursor/rules/workflow.mdc) (read this doc) and [.cursor/rules/engineering.mdc](../.cursor/rules/engineering.mdc) (code quality).

## Tool roles

| Tool | Owns |
|------|------|
| **ChatPRD** | Authoritative specs; optional cloud copy |
| **`prd/`** (in repo) | Committed specs agents and humans read |
| **Linear** | Backlog, cycles, issue status, priorities |
| **GitHub** | Code, branches, PRs, CI |

## End-to-end flow

Each step has an owner and an outcome. Skills named below are from the **ChatPRD** Cursor plugin.

### 1. `write-prd` — decide *what* to build

**When:** Starting the project, a new phase, or a major feature area.

**What happens:** You (with the agent) run the ChatPRD **write-prd** skill. It produces structured requirements—vision, phases, acceptance criteria—and saves them under `prd/`, starting with `prd/00-product-vision.md` and `prd/phase-N-….md` for the phase you are scoping.

**Outcome:** Committed specs in git. [prd/README.md](../prd/README.md) is updated with the **active phase** so agents know implementation is allowed.

---

### 2. `implement-from-prd` — plan *how* to build it

**When:** Before writing application code for a phase or large epic.

**What happens:** The **implement-from-prd** skill reads the relevant `prd/` doc and proposes a **milestone plan**: files to touch, order of work, risks. You review and approve (or adjust) before anyone edits code.

**Outcome:** Agreed implementation plan—no surprise architecture or scope creep mid-flight.

---

### 3. Linear — track *tasks* for humans

**When:** After you have a plan and want a backlog the team can prioritize.

**What happens:** Create a **parent epic per phase** and **child issues** from milestones. Each issue links to a `prd/…` section and lists acceptance criteria (see [Linear conventions](#linear-conventions)).

**Outcome:** Traceable work items. Linear holds status and assignment; it does **not** replace the PRD.

---

### 4. Code + GitHub PR — ship the change

**When:** Picking up a Linear issue (or an approved task without Linear).

**What happens:** Branch, implement against the issue’s acceptance criteria, open a PR using [.github/pull_request_template.md](../.github/pull_request_template.md). Follow [.cursor/rules/engineering.mdc](../.cursor/rules/engineering.mdc) while coding.

**Outcome:** Reviewable diff on GitHub, linked to Linear when applicable (`GYM-NN:` in title).

---

### 5. `check-prd-alignment` — verify *what* shipped matches spec

**When:** PR is ready for review or merge.

**What happens:** Run the **check-prd-alignment** skill against the relevant `prd/phase-*.md` section. It flags missing acceptance criteria, spec drift, and scope gaps.

**Outcome:** Confidence the merge matches product intent—not a substitute for code review or tests.

---

### 6. `update-prd` + close Linear — record reality

**When:** After merge (or phase complete).

**What happens:** **update-prd** updates ChatPRD / `prd/` if behavior differed from spec. Close the Linear issue; move deferred work into PRD **Future work** instead of silent backlog.

**Outcome:** Specs and tickets match what is actually in `main`.

---

Phases and detailed scope live in [prd/00-product-vision.md](../prd/00-product-vision.md) and [prd/README.md](../prd/README.md).

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

## ChatPRD plugin

Enable the **ChatPRD** Cursor plugin for this repo (product/requirements only—not code style).

| Intent | Skill |
|--------|--------|
| Write or expand specs | `write-prd` (save under `prd/`) |
| Plan implementation from a PRD | `implement-from-prd` |
| Pre-merge requirement check | `check-prd-alignment` |
| Record what shipped vs spec | `update-prd` |

## Engineering standards (code quality)

| Mechanism | Role |
|-----------|------|
| [.cursor/rules/engineering.mdc](../.cursor/rules/engineering.mdc) | Always-on agent guidance: minimal scope, simplicity, DRY, documentation, match conventions |
| **CI** (add when stack is chosen) | Automated format, lint, and tests on every PR |
| **Human PR review** | Architecture and design judgment |

Optional later: enable **Cursor Bugbot** on the repo for automated PR review once you have substantial code—it catches bugs and issues, not product scope.

Do **not** use ChatPRD skills for engineering style; they are for requirements and alignment only.

## Process rules (agents)

- Do not implement product features until [prd/README.md](../prd/README.md) names an active phase and the relevant `prd/` doc exists.
- Do not invent requirements or mark phases complete without updating `prd/`.
- Do not expand scope beyond the active Linear issue / PRD section without user approval.
- **Linear:** link `prd/…` and list acceptance criteria; do not paste the full PRD into the issue.
- **PRs:** note PRD deviations in the description, not only in chat.

## Agent session prompts (examples)

```text
Requirements pass: run write-prd; save under prd/; update prd/README.md active phase when approved.
```

```text
Working on Linear GYM-42. Read prd/phase-1-….md § "Run SQL". Propose a plan (implement-from-prd) before editing files.
```

```text
PR ready for GYM-42: run tests, check-prd-alignment against prd/phase-1-….md.
```

## Secrets

No secrets are committed. When the app is built, document required env vars in `.env.example`. On Cursor Cloud VMs, ask the user to add secrets in Cloud settings—do not assume a local `.env` exists.
