# Session state

Phase 5 uses the **practice workspace** with JSON APIs. Phase 6 keeps the same stores and routes; it types workspace context and splits the client modules. Phase 7 adds explain-on-fail (session-backed) without changing progress cookies. See [progress.md](progress.md) for the durable progress cookie.

## Stores

| Key / cookie | Holds | Lifetime |
|--------------|--------|----------|
| Starlette session `practice_attempts` | Draft SQL, run preview, grading per exercise | Browser session |
| `sql_gym_progress` cookie | Pass/attempt badges, best timed elapsed | 60 days |

Signing secret: `SESSION_SECRET` (required when `APP_ENV=production`). See `.env.example`.

## Practice attempts (`practice_attempts`)

Per-exercise map keyed by `exercise_id`:

- `sql` — last editor text
- `query_result` — bounded preview (max **25 rows** in session; full execution up to 500 rows server-side)
- `execution_error` — last run error
- `grading` — last submit outcome
- `status` — `draft`, `submitted`, or `graded`

Session preview cap prevents large grids from exceeding browser cookie limits while grading still re-executes SQL on submit.

**Explain-on-fail (Phase 7):** `POST .../explain` uses `get_failed_submit_attempt` — only when the session’s last grading for that exercise has `passed: false`. A subsequent **Run** clears grading from the attempt (draft status), so explain returns “no failed submit” until another failing submit.

## Workspace APIs

Registered via `APIRouter` prefix `/api/practice` (`src/app/api/routes.py`):

| Route | Purpose |
|-------|---------|
| `GET /api/practice/exercises` | Filtered exercise list for drawer |
| `GET /api/practice/{dataset}/{exercise}` | Exercise payload + attempt restore |
| `POST /api/practice/{dataset}/{exercise}/run` | Execute SQL → JSON grid or error |
| `POST /api/practice/{dataset}/{exercise}/submit` | Grade → JSON + `Set-Cookie` progress |
| `POST /api/practice/{dataset}/{exercise}/explain` | Explain last failed submit → `{explanation}` or `{error:{message}}` (no progress cookie change) |
| `POST /api/practice/progress/clear` | Clear progress cookie |

`GET` exercise payloads are built from typed `WorkspaceContext` (`src/app/workspace/context.py`).

Explain context is built server-side from the exercise catalog + session attempt (prompt, output requirements, learner SQL, grading summary, expected **column names**). It does **not** include `reference_sql` or expected row values.

## Pages

| Route | Purpose |
|-------|---------|
| `GET /` | Redirect → `/practice` |
| `GET /practice` | Redirect → first eligible exercise workspace |
| `GET /practice/{dataset}/{exercise}` | Workspace shell (SSR + client patches) |
| `GET /practice/interview/*` | Legacy redirect → `/practice` |

Exercise switching restores draft SQL, last run console output, and grading metadata from session via the exercise API. The grading modal is shown only on fresh submit, not on exercise switch. On a **failed graded** submit, the modal offers **Explain with AI** (opt-in fetch to the explain route).

## Client modules

| Path | Role |
|------|------|
| `static/js/practice-workspace-entry.js` | DOMContentLoaded → `initPracticeWorkspace` |
| `static/js/practice-workspace.js` | Thin orchestrator (run/submit/clear wiring) |
| `static/js/workspace/format.js` | Shared `formatTime` (`M:SS`) + `formatCell` |
| `static/js/workspace/api-client.js` | Config + practice API URL helpers (including explain) |
| `static/js/workspace/render.js` | Console, progress UI, grading modal (+ explain), exercise apply |
| `static/js/workspace/stopwatch.js` | Elapsed timer |
| `static/js/workspace/navigation.js` | Drawer, prev/next, filter redirect, history |

Initial `workspace_config` JSON is derived from `WorkspaceContext` (dataset/exercise ids, filters, navigation, attempt preview, progress).

## Ollama process lifecycle (not browser session)

Model pull/cleanup is tied to the **uvicorn app process**, not the browser tab:

- Startup: best-effort pull of `OLLAMA_MODEL`
- Shutdown: best-effort delete if this process pulled it (unless `OLLAMA_KEEP_MODEL`)

See [README.md](../README.md) and [phase-7-manual-test-plan.md](phase-7-manual-test-plan.md).
