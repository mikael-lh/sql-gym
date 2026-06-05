---
name: sql-gym-pre-review-fix
description: Apply blocking pre-review findings on the branch — fix, test, deslop, push. Use after sql-gym-pre-review-reviewer; then re-run reviewer until pass.
---

# sql-gym: pre-review fix

**Implementer role.** Address **blocking** findings from **`sql-gym-pre-review-reviewer`** on the **same branch** as the PR. Do **not** check pre-review boxes or mark ready for **user** review—that happens after a clean reviewer pass and final verification.

## Inputs

Ask if missing:

- PR URL or branch name
- Linear issue id (`TIM-NN`)
- Link or paste of **`## Pre-review findings (pass N)`** (blocking items)

If there are no reviewer findings yet, run **sql-gym-pre-review-reviewer** first (in a **different** agent/session).

## Steps

1. Checkout the PR branch.
2. For each **blocking** item from the latest reviewer pass, implement the fix. Do **not** expand scope beyond the issue / PRD without **user** approval.
3. cursor-team-kit **`deslop`** on changed code (or N/A — docs-only).
4. Run tests/lint (or manual equivalent); fix until green.
5. Commit, push, and update the PR description with what changed (e.g. “Pre-review fix pass 2 — …”).
6. Tell the **user** to run **`sql-gym-pre-review-reviewer`** again in a **new** agent/session (or Task readonly subagent). Increment pass number.

## Stop

Do **not** mark the PR ready for **user** review until **sql-gym-pre-review** completes (reviewer reports no blocking items + final checklist).

Do **not** merge.

## References

- [sql-gym-pre-review-reviewer](../sql-gym-pre-review-reviewer/SKILL.md)
- [sql-gym-implement-issue](../sql-gym-implement-issue/SKILL.md) — same coding standards
- [.cursor/rules/engineering.mdc](../../../.cursor/rules/engineering.mdc)
