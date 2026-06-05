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

1. Run **sql-gym-pre-review-reviewer** via a **Task** subagent (**readonly**) or ask the **user** to start a **new** agent with the PR link.
2. If blocking findings exist, either run **sql-gym-pre-review-fix** yourself (fixer hat) **or** ask the **user** to run it in the implementer agent—then **never** approve your own fixes without a **new** reviewer pass.
3. After reviewer reports **no blocking items**, run tests/lint/deslop if not already green, update the PR description, check **Agent pre-review** boxes, mark ready for **user** review.

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
- A required plugin is unavailable **and** manual fallback is insufficient to make a confident judgment (e.g. complex alignment question that needs ChatPRD context)

When a plugin is unavailable but a manual fallback was used, document which tool was skipped and which fallback was applied — do **not** silently mark that box passed. Leave it unchecked; note it in the PR description.

Leave boxes **unchecked** and PR **draft**.

## Stop

Do not merge. The **user** performs final review and merge.

## References

- [docs/WORKFLOW.md](../../../docs/WORKFLOW.md#pre-review-before-user-review)
- [.cursor/rules/workflow.mdc](../../../.cursor/rules/workflow.mdc)
