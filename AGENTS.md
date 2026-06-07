# Agent instructions

## Cursor Cloud specific instructions

SQL Gym is a **Phase 0 Python/FastAPI scaffold** — no database, auth, or external services are required for local development.

### Stack

- Python 3.12, managed with [`uv`](https://docs.astral.sh/uv/) (`pyproject.toml`, `uv.lock`)
- FastAPI + Uvicorn dev server, Jinja2 templates, static CSS
- Tests use in-process ASGI transport (no running server needed for `pytest`)

### Dependency refresh

On VM startup, `uv sync --locked` runs automatically. `uv` is installed under `~/.local/bin` (login shells include it on PATH).

### Run the app

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Alternative entrypoint: `uv run sql-gym`

| Route | Purpose |
|-------|---------|
| `GET /` | Landing page |
| `GET /practice` | Practice placeholder flow |
| `GET /health` | Health check (`{"status": "ok"}`) |
| `/static/*` | CSS and static assets |

### Lint, types, tests, build

See [README.md](README.md) for the canonical commands:

| Purpose | Command |
|---------|---------|
| Lint | `uv run ruff check .` |
| Types | `uv run mypy .` |
| Tests | `uv run pytest` |
| Package build | `uv build` |

### Full repo validation

`./scripts/validate-env.sh` also checks PRD/skills files, `gh auth status`, and the origin remote. Those checks can fail in Cloud VMs without GitHub CLI auth — the app stack checks (`uv sync`, build, ruff, mypy, pytest) are the ones that matter for development.

### Gotchas

- **Detached HEAD:** Cloud agents may start on a detached commit; create a feature branch before committing (`cursor/<name>-4b86`).
- **No Docker/Compose:** Everything runs directly on the VM.
- **CI not configured yet:** Rely on local ruff/mypy/pytest before PR handoff.
