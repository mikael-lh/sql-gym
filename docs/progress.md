# Browser-local progress

Phase 3 stores learner progress in a signed HTTP-only cookie — no accounts required.

## Cookie

| Property | Value |
|----------|--------|
| Name | `sql_gym_progress` |
| Lifetime | 60 days (`max_age=5184000`), refreshed on each progress write |
| Signing | `SESSION_SECRET` (same material as Starlette sessions) |
| Scope | Device/browser only; clearing cookies resets progress |

## Payload (v1)

```json
{
  "v": 1,
  "exercises": {
    "times-archive-003": {
      "status": "passed",
      "passed_at": "2026-06-09T12:00:00+00:00",
      "elapsed_seconds": 420
    }
  }
}
```

Statuses: `attempted`, `passed` (absent entry = `not_started`).

## Write triggers

- `POST /api/practice/{dataset}/{exercise}/submit` after grading
- `POST /api/practice/progress/clear`

Not written on `POST …/run` or ordinary page views.

## Session vs progress

| Store | Holds | Lifetime |
|-------|--------|----------|
| Session cookie | Draft SQL, last run, last grade | Browser session |
| Progress cookie | Pass/attempt badges, best timed elapsed | 60 days |

Workspace APIs and session restore: [session-state.md](session-state.md).

## Privacy

Progress is anonymous and local. No server-side learner database in Phase 3.
