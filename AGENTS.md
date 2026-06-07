# Agent environment notes

## Cursor Cloud specific instructions

### Stack

SQL Gym is a **Python 3.12 + FastAPI** web app managed with [`uv`](https://docs.astral.sh/uv/). Phase 0 is a server-rendered scaffold only — no database, auth, or SQL execution yet. See [README.md](README.md) and [prd/README.md](prd/README.md).

### Prerequisites

- **Python 3.12** (system `python3.12` is fine)
- **`uv`** on `PATH` (install once per VM if missing: `curl -LsSf https://astral.sh/uv/install.sh | sh`, then `export PATH="$HOME/.local/bin:$PATH"`)

### Dependency sync

From repo root:

```bash
uv sync --locked
```

### Run the dev server

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Default bind in `app.main:main()` is `127.0.0.1:8000`; use `--host 0.0.0.0` when the app must be reachable outside localhost (e.g. Cloud VM browser checks).

Key routes: `/` (landing), `/practice` (placeholders), `/health` (`{"status":"ok"}`), `/static/*`.

### Lint, typecheck, tests, full validation

| Purpose | Command |
|---------|---------|
| Lint | `uv run ruff check .` |
| Types | `uv run mypy .` |
| Tests | `uv run pytest` |
| Package build | `uv build` |
| Full workflow + stack check | `./scripts/validate-env.sh` |

`./scripts/validate-env.sh` also checks PRD/skills files, `gh auth`, and git remote — useful for agent workflow validation, not required for app-only smoke tests.

### Services

| Service | Required? | Notes |
|---------|-----------|-------|
| FastAPI (Uvicorn) | Yes (manual/browser E2E) | Single process; port **8000** |
| PostgreSQL | No | Future phase; dialect is metadata only in Phase 0 |
| Docker / compose | No | Not used in this repo |

`pytest` uses in-process `httpx.ASGITransport` — no running server needed for the test suite.

### Gotchas

- **`uv` not on PATH**: After install, source `$HOME/.local/bin/env` or add `$HOME/.local/bin` to `PATH` in the shell running dev commands.
- **Detached HEAD**: Cloud VMs may start detached; checkout `main` or a feature branch before git workflow checks matter.
- **No `.env` for Phase 0**: The app has no runtime secrets; do not commit secrets. Future phases should document vars in `.env.example`.
