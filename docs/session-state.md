# Session state

Phase 4 adds **interview sessions** alongside existing practice attempt storage. See also [progress.md](progress.md) for the durable progress cookie.

## Stores

| Key / cookie | Holds | Lifetime |
|--------------|--------|----------|
| Starlette session `practice_attempts` | Draft SQL, run preview, grading per exercise | Browser session |
| Starlette session `interview_session` | Interview queue, index, outcomes | Browser session |
| `sql_gym_progress` cookie | Pass/attempt badges, best timed elapsed | 60 days |

Interview session state is **not** written to the progress cookie. Each submit still updates progress per Phase 3 rules.

## Practice attempts (`practice_attempts`)

Per-exercise map keyed by `exercise_id`:

- `sql` — last editor text
- `query_result` — bounded preview (max **25 rows** in session; full execution up to 500 rows server-side)
- `execution_error` — last run error
- `grading` — last submit outcome
- `status` — `draft`, `submitted`, or `graded`

Session preview cap prevents large grids from exceeding browser cookie limits while grading still re-executes SQL on submit.

## Interview session (`interview_session`)

Payload v1:

```json
{
  "v": 1,
  "queue": ["times-archive-001", "times-archive-002"],
  "current_index": 0,
  "queue_mode": "fixed",
  "requested_length": 3,
  "difficulty": null,
  "started_at": "2026-06-09T12:00:00+00:00",
  "outcomes": {
    "times-archive-001": { "passed": true, "elapsed_seconds": 125 }
  },
  "status": "active"
}
```

| Field | Meaning |
|-------|---------|
| `queue_mode` | `fixed` (3/5/8) or `unlimited` |
| `requested_length` | `null` when unlimited |
| `status` | `active`, `ended_early`, or `completed` |
| `outcomes` | Pass/fail and optional elapsed per exercise id |

Summary GET clears `interview_session` after render. **Abandon session** clears it immediately.

## Routes

| Route | Purpose |
|-------|---------|
| `GET /practice/interview/start` | Configure queue |
| `POST /practice/interview/start` | Create session → first question |
| `GET /practice/interview/{dataset}/{exercise}` | Interview exercise page |
| `POST …/run`, `POST …/submit` | Same semantics as practice paths |
| `POST /practice/interview/next` | Advance after grading |
| `POST /practice/interview/end` | End early → summary |
| `POST /practice/interview/abandon` | Clear session → `/practice` |
| `GET /practice/interview/summary` | Recap (clears session) |

Guards redirect to the current queued exercise when the URL exercise id does not match `queue[current_index]`.
