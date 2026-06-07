# Agent instructions

sql-gym has **product vision and Phase 0 PRD** committed under `prd/`, plus repo-local PRD skills and Linear backlog. **No application code or dependency manifests exist yet** — Phase 0 scaffolding is drafted, not implemented.

## Cursor Cloud specific instructions

### What runs today

There is **no runnable application** (no backend, frontend, dev server, lint, or test commands). Product implementation is blocked until Phase 0 is **approved** and `prd/README.md` names **Phase 0** as the active phase.

What **does** work in Cloud:

| Capability | How to verify |
|------------|---------------|
| Repo + git | `git status`; branch naming `cursor/<desc>-<suffix>` per [docs/WORKFLOW.md](docs/WORKFLOW.md) |
| GitHub PRs | `gh auth status`; use [.github/pull_request_template.md](.github/pull_request_template.md) |
| Linear MCP | `get_issue` for `TIM-16` or `list_issues` with `project: sql-gym` |
| Repo skills | Nine skills under `.cursor/skills/` — invoke by name (see [README.md](README.md)) |
| Environment check | `./scripts/validate-env.sh` from repo root |

### PRD workflow (repo-local — no ChatPRD required)

Product specs use **committed markdown in `prd/`** and repo-local skills:

| Skill | Purpose |
|-------|---------|
| `write-prd` | Create or revise PRDs under `prd/` |
| `implement-from-prd` | Milestone plan from a PRD (before code) |
| `check-prd-alignment` | Pre-merge spec alignment |
| `update-prd` | Record what shipped vs spec |

Do **not** call ChatPRD MCP for product work unless the user explicitly asks.

### MCP plugins

| Plugin | Cloud status | Notes |
|--------|--------------|-------|
| **Linear** | Connected | Issue prefix `TIM-`; project [sql-gym](https://linear.app/times-api/project/sql-gym-ce6a8985c99e) |
| **Superpowers** | Optional | Implementation/review during builds — install in Cursor marketplace |
| **cursor-team-kit** | Optional | `deslop` pass on changed code |

If Linear-backed issue lookup fails, check MCP auth in Cursor settings.

### Lint / test / CI

**CI is not configured yet.** There are no `pyproject.toml`, `package.json`, Makefile, or Docker files. Pre-review checklists should state "CI not configured — ran `./scripts/validate-env.sh`".

When Phase 0 is implemented (see [prd/phase-0-product-scaffolding.md](prd/phase-0-product-scaffolding.md)), update this section and the VM update script with install, lint, test, and dev-server commands.

### Workflow gates (always enforced)

See [.cursor/rules/workflow.mdc](.cursor/rules/workflow.mdc):

- No product features without active phase + matching `prd/` doc.
- No application code until user approves a local `implement-from-prd` plan (`sql-gym-start-issue`).
- Branch naming: `cursor/<short-desc>-<suffix>` only.

**Current state:** Phase 0 PRD is **draft**; active phase in [prd/README.md](prd/README.md) is **None**.

### Starting work

1. Vision: [prd/00-product-vision.md](prd/00-product-vision.md) (merged).
2. Next: approve [prd/phase-0-product-scaffolding.md](prd/phase-0-product-scaffolding.md), set active phase in `prd/README.md`.
3. Pick up an issue: `sql-gym-start-issue for TIM-NN` (plan only; stops for approval).
4. After approval: `sql-gym-implement-issue for TIM-NN`.
5. Before user review: `sql-gym-pre-review for TIM-NN`.

Full playbook: [docs/WORKFLOW.md](docs/WORKFLOW.md).

### Secrets

No secrets are committed. When the app is built, document env vars in `.env.example`. Ask the user to add secrets in Cloud settings — do not assume a local `.env` exists.
