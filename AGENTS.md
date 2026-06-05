# Agent instructions

sql-gym is in **early setup**: workflow docs, Cursor skills, and Linear backlog exist; **no application code or dependency manifests yet**.

## Cursor Cloud specific instructions

### What runs today

There is **no runnable application** (no backend, frontend, API, database, or dev server). Product E2E testing is blocked until `prd/00-product-vision.md` exists and an active phase is named in `prd/README.md`.

What **does** work in Cloud:

| Capability | How to verify |
|------------|---------------|
| Repo + git | `git status`; branch naming `cursor/<desc>-<suffix>` per [docs/WORKFLOW.md](docs/WORKFLOW.md) |
| GitHub PRs | `gh auth status`; use [.github/pull_request_template.md](.github/pull_request_template.md) |
| Linear MCP | `get_issue` for `TIM-16` or `list_issues` with `project: sql-gym` |
| Repo skills | Five skills under `.cursor/skills/sql-gym-*` — invoke by name (see [README.md](README.md)) |
| Environment check | `./scripts/validate-env.sh` from repo root |

### MCP plugins

| Plugin | Cloud status | Notes |
|--------|--------------|-------|
| **Linear** | Connected | Issue prefix `TIM-`; project [sql-gym](https://linear.app/times-api/project/sql-gym-ce6a8985c99e) |
| **ChatPRD** | Requires Pro/Team | MCP tools return a subscription error without Pro/Team. Use local Cursor with ChatPRD for `write-prd`, `implement-from-prd`, `check-prd-alignment`, `update-prd`. |
| **Superpowers** | Optional | Implementation/review during builds — install in Cursor marketplace |
| **cursor-team-kit** | Optional | `deslop` pass on changed code |

If a skill fails in Cloud, check MCP auth in Cursor settings before assuming repo misconfiguration.

### Lint / test / CI

**CI is not configured yet** (per [docs/WORKFLOW.md](docs/WORKFLOW.md)). There are no `pyproject.toml`, `package.json`, Makefile, or Docker files. Pre-review checklists should state "CI not configured — ran `./scripts/validate-env.sh`" (or future stack commands once added).

When the stack lands (likely Python + DuckDB per `.gitignore`), update this section with:

- Dependency install command (e.g. `uv sync` or `pip install -e ".[dev]"`)
- Lint: e.g. `ruff check .`
- Test: e.g. `pytest`
- Dev server / CLI entrypoint

### Workflow gates (always enforced)

See [.cursor/rules/workflow.mdc](.cursor/rules/workflow.mdc):

- No product features without active phase + matching `prd/` doc.
- No application code until user approves an `implement-from-prd` plan (`sql-gym-start-issue`).
- Branch naming: `cursor/<short-desc>-<suffix>` only.

### Starting work

1. Requirements epic: [TIM-16](https://linear.app/times-api/issue/TIM-16/requirements-or-product-vision-write-prd) — run `write-prd`, commit under `prd/`.
2. Pick up an issue: `sql-gym-start-issue for TIM-NN` (plan only; stops for approval).
3. After approval: `sql-gym-implement-issue for TIM-NN`.
4. Before user review: `sql-gym-pre-review for TIM-NN`.

Full playbook: [docs/WORKFLOW.md](docs/WORKFLOW.md).

### Secrets

No secrets are committed. When the app is built, document env vars in `.env.example`. Ask the user to add secrets in Cloud settings — do not assume a local `.env` exists.
