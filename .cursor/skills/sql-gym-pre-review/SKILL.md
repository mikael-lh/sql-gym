---
name: sql-gym-pre-review
description: Orchestrate agent pre-review — independent reviewer, fixer loop until pass, then checklist and handoff to user. Use after sql-gym-implement-issue.
---

# sql-gym: pre-review (orchestrator)

Run before marking a PR ready for **user** review. Does **not** replace **user** judgment on product/architecture.

**Two roles:** a **reviewer** agent (no writes) and a **fixer** agent (commits on the branch). The agent that **implemented** the PR must **not** perform the judgment review alone.

## Default flow

```text
implement-issue → draft PR
  → pre-review-reviewer (pass 1)     [independent agent / new chat / readonly Task]
  → if blocking: pre-review-fix       [implementer agent]
  → pre-review-reviewer (pass 2+)     [independent again]
  → repeat until reviewer: no blocking
  → final verification (tests/lint/deslop) + check PR boxes + ready for user
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
4. After a pass reports **no blocking items**, run tests/lint/deslop if not already green, update the PR description, check **Agent pre-review** boxes, mark ready for **user** review.

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

Leave boxes **unchecked** and PR **draft**.

## Stop

Do not merge. The **user** performs final review and merge.

## References

- [docs/WORKFLOW.md](../../../docs/WORKFLOW.md#pre-review-before-user-review)
- [.cursor/rules/workflow.mdc](../../../.cursor/rules/workflow.mdc)
