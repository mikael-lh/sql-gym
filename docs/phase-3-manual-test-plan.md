# Phase 3 manual test plan

End-to-end checklist for cookie progress and timed exercise mode.

## Prerequisites

1. Complete [Phase 2 manual test plan](phase-2-manual-test-plan.md) prerequisites (Postgres, import, app running with `DATABASE_URL` and `SESSION_SECRET`).
2. `uv run uvicorn app.main:app --reload` with `.env` loaded.

## Progress cookie

| Step | Action | Expected |
|------|--------|----------|
| 1 | Open `/practice` | Shows `0 of 50 exercises passed` and progress badges `Not started`. |
| 2 | Pass an exercise via submit | Badge becomes `Passed` on catalog card after redirect. |
| 3 | Close browser completely, reopen `/practice` | Passed badge still visible (60-day cookie). |
| 4 | Click **Continue practicing** | Opens next unpassed exercise in catalog order. |
| 5 | Filter difficulty to `Beginner`, click continue | Next unpassed **Beginner** exercise only. |
| 6 | Click **Clear my progress** on `/practice` | All badges reset to `Not started`. |

## Timed mode

| Step | Action | Expected |
|------|--------|----------|
| 1 | Open `/practice/times-archive/times-archive-005` (Timed) | Timer panel with **Start timed exercise**. |
| 2 | Click start | Countdown shows `mm:ss` from `estimated_time_minutes`. |
| 3 | Submit correct SQL before timeout | Pass feedback; best time shown on preview when passed. |
| 4 | Retry with faster pass | `Passed` remains; best time updates if lower. |
| 5 | Let timer reach `0:00` | Auto-submit runs; grading feedback appears. |

## References

- [progress.md](progress.md)
- [prd/phase-3-progress-and-timed-mode.md](../prd/phase-3-progress-and-timed-mode.md)
