# Session state

Phase 5 uses the **practice workspace** with JSON APIs. See [progress.md](progress.md) for the durable progress cookie.

## Stores

| Key / cookie | Holds | Lifetime |
|--------------|--------|----------|
| Starlette session `practice_attempts` | Draft SQL, run preview, grading per exercise | Browser session |
| `sql_gym_progress` cookie | Pass/attempt badges, best timed elapsed | 60 days |

## Practice attempts (`practice_attempts`)

Per-exercise map keyed by `exercise_id`:

- `sql` — last editor text
- `query_result` — bounded preview (max **25 rows** in session; full execution up to 500 rows server-side)
- `execution_error` — last run error
- `grading` — last submit outcome
- `status` — `draft`, `submitted`, or `graded`

Session preview cap prevents large grids from exceeding browser cookie limits while grading still re-executes SQL on submit.

## Workspace APIs

| Route | Purpose |
|-------|---------|
| `GET /api/practice/exercises` | Filtered exercise list for drawer |
| `GET /api/practice/{dataset}/{exercise}` | Exercise payload + attempt restore |
| `POST /api/practice/{dataset}/{exercise}/run` | Execute SQL → JSON grid or error |
| `POST /api/practice/{dataset}/{exercise}/submit` | Grade → JSON + `Set-Cookie` progress |
| `POST /api/practice/progress/clear` | Clear progress cookie |

## Pages

| Route | Purpose |
|-------|---------|
| `GET /` | Redirect → `/practice` |
| `GET /practice` | Redirect → first eligible exercise workspace |
| `GET /practice/{dataset}/{exercise}` | Workspace shell (SSR + client patches) |
| `GET /practice/interview/*` | Legacy redirect → `/practice` |

Exercise switching restores draft SQL, last run console output, and grading metadata from session via the exercise API. The grading modal is shown only on fresh submit, not on exercise switch.
