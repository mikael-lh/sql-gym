# Agent instructions

Guidance for AI agents working in this repository.

## Cursor Cloud specific instructions

### Stack

Single-service **Python 3.12 + FastAPI** app (Phase 0 scaffold). Package management via [`uv`](https://docs.astral.sh/uv/) (`pyproject.toml`, `uv.lock`). No Node.js, Docker, or external databases required for local dev.

### `uv` on Cloud VMs

`uv` is installed at `~/.local/bin/uv`. Ensure `~/.local/bin` is on `PATH`, or invoke `/home/ubuntu/.local/bin/uv` directly.

### Install dependencies

From repo root:

```bash
uv sync --locked
```

### Run the dev server

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Alternate entrypoint: `uv run sql-gym` (binds `127.0.0.1:8000` only).

### Lint, typecheck, tests, build

See [README.md](README.md). Quick reference:

| Check | Command |
|-------|---------|
| Lint | `uv run ruff check .` |
| Types | `uv run mypy .` |
| Tests | `uv run pytest` |
| Build | `uv build` |

Tests use in-process `httpx.ASGITransport` — no running server required for pytest.

### Full validation script

`./scripts/validate-env.sh` also checks PRD/skills layout and **`gh auth status`**. GitHub CLI auth may fail on Cloud VMs without credentials; that does not block running the app. Use the individual `uv` commands above when `gh` is unavailable.

### Hello-world smoke (manual)

With the dev server running:

- `http://127.0.0.1:8000/` — home page ("Phase 0 app shell")
- `http://127.0.0.1:8000/practice` — Times Archive demo placeholders
- `http://127.0.0.1:8000/health` — `{"status":"ok"}`

Phase 0 has no SQL execution, grading, or persistence — UI placeholders only.

### Workflow

Product work follows `prd/` and repo skills; see [README.md](README.md) and [.cursor/rules/workflow.mdc](.cursor/rules/workflow.mdc).
