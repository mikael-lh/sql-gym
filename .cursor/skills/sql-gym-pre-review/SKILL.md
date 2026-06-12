---
name: sql-gym-pre-review
description: Use after sql-gym-implement-issue when a PR needs independent pre-review before handoff or authorized autonomous merge.
---

# sql-gym: pre-review (orchestrator)

Run before marking a PR ready for **user** review or authorized autonomous merge. Does **not** replace **user** judgment on product/architecture.

**Two roles:** a **reviewer** agent (no writes) and a **fixer** agent (commits on the branch). The agent that **implemented** the PR must **not** perform the judgment review alone.

## Default flow

```text
implement-issue → draft PR
  → pre-review-reviewer (pass 1)     [independent agent / new chat / readonly Task]
  → if blocking: pre-review-fix       [implementer agent]
  → pre-review-reviewer (pass 2+)     [independent again]
  → repeat until reviewer: no blocking
  → final verification (tests/lint/deslop) + check PR boxes + ready for handoff or authorized merge
```

| Skill | Role | Writes branch? |
|-------|------|----------------|
| **sql-gym-pre-review-reviewer** | Alignment + code review findings | **No** |
| **sql-gym-pre-review-fix** | Apply blocking fixes + tests/deslop | **Yes** |
| **This skill** | Coordinate the loop and final handoff | As fixer only when no separate fixer is used |

**Docs-only PRs:** Reviewer may mark code tools N/A; fixer runs only if needed.

## When you are the orchestrator (single session)

If the **user** invoked **`sql-gym-pre-review`** in the implementer session:

1. Run a review pass per **sql-gym-pre-review-reviewer** via a **Task** subagent (**readonly**) or follow that skill’s steps yourself in reviewer mode—do not self-approve in the implementer voice.
2. Post each pass under **`## Pre-review findings (pass N)`** on the PR (blocking list, `Nit:` list, fix required yes/no).
3. If blocking findings exist, run **sql-gym-pre-review-fix** (fixer hat) on the branch, then run another review pass before treating fixes as done.
4. After a pass reports **no blocking items**, run tests/lint/deslop if not already green, update the PR description, check **Agent pre-review** boxes, and mark ready for **user** review or authorized autonomous merge.

Do **not** check boxes or ask for **user** review while blocking reviewer findings remain.

## Blocking vs non-blocking

| Kind | Owner | Action |
|------|-------|--------|
| **Blocking** | Reviewer lists | Fixer addresses on branch; re-run reviewer |
| **`Nit:`** | Reviewer lists | Optional; may remain at handoff |

## Escalate to the user

- Product/architecture decision or approved PRD deviation needed
- Cannot run independent reviewer (no Task, same session only)
- Stuck after multiple reviewer/fix cycles
- The linked PRD is missing, ambiguous, or insufficient to make a confident alignment judgment

When a plugin is unavailable but a manual fallback was used, document which tool was skipped and which fallback was applied — do **not** silently mark that box passed. Leave it unchecked; note it in the PR description.

Leave boxes **unchecked** and PR **draft**.

## Stop

Do not merge (per [workflow.mdc](../../rules/workflow.mdc) gates). The **user** or an explicitly authorized orchestration skill performs final merge.

## Handoff checklist

Check **Agent pre-review** boxes on the PR only after a reviewer pass reports no blocking items and verification is green. Boxes match [.github/pull_request_template.md](../../../.github/pull_request_template.md):

- `check-prd-alignment` vs linked `prd/` section
- Superpowers `code-reviewer` vs approved plan + [engineering.mdc](../../../.cursor/rules/engineering.mdc) (or N/A docs-only)
- [google-eng-practices](../../../docs/references/google-eng-practices.md) review (blocking fixed; `Nit:` optional)
- cursor-team-kit `deslop` (or N/A docs-only)
- Tests/lint green, or state **CI not configured yet** and note what ran (e.g. `./scripts/validate-env.sh`)
- Playwright workspace browser checks — `uv run pytest tests/test_grading_modal.py tests/test_workspace_console_scroll.py` (or **N/A** — no workspace UI in PR)

PR description must include: summary, risks, test plan, PRD deviations, and any remaining **`Nit:`** items.

## References

- [sql-gym-pre-review-reviewer](../sql-gym-pre-review-reviewer/SKILL.md)
- [sql-gym-pre-review-fix](../sql-gym-pre-review-fix/SKILL.md)
- [.github/pull_request_template.md](../../../.github/pull_request_template.md)
- [.cursor/rules/workflow.mdc](../../../.cursor/rules/workflow.mdc) — gate only
