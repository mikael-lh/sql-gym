# Strict grid-match grading

Phase 2 grades learner SQL by comparing the executed result grid to a committed expected grid for each catalog exercise.

## Rules

1. **Column names and order** must match exactly.
2. **Row count** must match exactly.
3. **Cell values** must match. For most exercises, **row order does not matter** (unordered multiset compare). Exercises that explicitly require sorted output use strict row-order grading.
4. **No partial credit** — any mismatch is a fail.

Per-exercise `grading_row_order` in the catalog:

| Mode | Exercises | Behavior |
|------|-----------|----------|
| `multiset` | 48 (default) | Same rows in any order |
| `strict` | `times-archive-023`, `times-archive-039` | Prompt requires explicit sort order |

## NULL and formatting

- SQL `NULL` is stored as JSON `null` in expected grids and normalized to Python `None` in execution results.
- Empty strings are compared as returned by PostgreSQL; `NULL` and `''` are not treated as equal.
- Dates are compared as ISO `YYYY-MM-DD` strings.
- Decimals from PostgreSQL are normalized to `int` when whole, otherwise `float`, before comparison.

## Truncation

Learner queries are capped at **500 rows**. If the executed result is truncated, grading fails with a learner-safe message even when the visible rows match.

Queries are cancelled after **30 seconds** by default (`SQL_STATEMENT_TIMEOUT_MS` in `.env` overrides this).

## Failure messages

Summaries are intentionally generic (for example, "Row count does not match") and do not reveal expected answers.

## Regenerating expected grids

Expected grids are generated from each exercise's `reference_sql` against imported Times Archive data:

```bash
./scripts/generate-expected-results.sh
```

See [times-data-setup.md](times-data-setup.md).
