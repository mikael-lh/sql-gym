---
name: sql-gym-pre-review-fix
description: Apply blocking pre-review findings on the branch — fix, test, deslop, push. Used by sql-gym-pre-review orchestrator or standalone after a review pass.
---

# sql-gym: pre-review fix

**Implementer role.** Address **blocking** findings from a review pass on the **same branch** as the PR. Do **not** check pre-review boxes or mark ready for **user** review—that is **`sql-gym-pre-review`** after the loop passes.

## Inputs

Ask if missing:

- PR URL or branch name
- Linear issue id (`TIM-NN`)
- Link or paste of **`## Pre-review findings (pass N)`** (blocking items)

If there are no reviewer findings yet, run **`sql-gym-pre-review`** (or a review pass via that orchestrator) first.

## Steps

1. Checkout the PR branch.
2. For each **blocking** item from the latest reviewer pass, implement the fix. Do **not** expand scope beyond the issue / PRD without **user** approval.
3. cursor-team-kit **`deslop`** on changed code (or N/A — docs-only). **If cursor-team-kit is unavailable**, do a manual slop pass: remove redundant comments, dead code, and AI-ism phrasing; note "manual deslop (cursor-team-kit unavailable)" in the PR description and leave the deslop PR box **unchecked**.
4. Run tests/lint (or manual equivalent); fix until green. When the PR touches workspace UI, also run `uv run pytest tests/test_grading_modal.py tests/test_workspace_console_scroll.py -v` (install Chromium via `uv run playwright install chromium` if needed).
5. Commit, push, and update the PR description with what changed (e.g. “Pre-review fix pass 2 — …”).
6. Hand back to **`sql-gym-pre-review`** for the next review pass (or tell the **user** to run it). Increment pass number in the PR notes when helpful.

## Stop

Do **not** mark the PR ready for **user** review until **sql-gym-pre-review** completes (reviewer reports no blocking items + final checklist).

Do **not** merge (per [workflow.mdc](../../rules/workflow.mdc) gates).

## References

- [sql-gym-pre-review](../sql-gym-pre-review/SKILL.md) — orchestrator and handoff
- [sql-gym-pre-review-reviewer](../sql-gym-pre-review-reviewer/SKILL.md)
- [sql-gym-implement-issue](../sql-gym-implement-issue/SKILL.md) — same coding standards
- [.cursor/rules/engineering.mdc](../../../.cursor/rules/engineering.mdc)
