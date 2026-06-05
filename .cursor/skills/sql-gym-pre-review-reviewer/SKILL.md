---
name: sql-gym-pre-review-reviewer
description: Independent agent pre-review (read-only) — alignment and code review findings only. Use in a new agent/session or Task subagent; do not commit. Pair with sql-gym-pre-review-fix for fixes.
---

# sql-gym: pre-review reviewer

**Review only.** Produce findings; do **not** edit the branch, commit, push, check PR boxes, or mark the PR ready for **user** review.

## Independence (required)

The reviewer must **not** be the same agent that implemented the PR.

| Situation | What to do |
|-----------|------------|
| **New agent / new chat / Cloud Agent handoff** | Preferred — pass PR URL, branch, `TIM-NN`, linked `prd/` section, and the approved implementation plan. |
| **Same session as implementer** | Launch a **Task** subagent (`code-reviewer` or `explore`, **readonly**) with only PR + plan + `prd/` context. Use **its** output as the review; do not self-review in the implementer voice. |
| **Cannot get independent review** | Escalate to the **user**; leave pre-review boxes unchecked. |

## Inputs

Ask if missing:

- PR URL or branch name
- Linear issue id (`TIM-NN`) and linked `prd/` section
- Approved implementation plan (from **sql-gym-start-issue** / `implement-from-prd`)
- Pre-review pass number (default 1)

## Steps

1. Read the PR diff, description, and linked `prd/phase-*.md` section. Do **not** assume unstated intent from the implementer.
2. ChatPRD **`check-prd-alignment`** — missing AC, spec drift, deviations.
3. Superpowers **`code-reviewer`** vs the approved plan and [engineering.mdc](../../../.cursor/rules/engineering.mdc).
4. Review the diff against [docs/references/google-eng-practices.md](../../../docs/references/google-eng-practices.md). Use **`Nit:`** only for non-blocking items.
5. **Triage** every item as **blocking** or **`Nit:`**.
6. Post results under **`## Pre-review findings (pass N)`** in the PR description or a PR comment. Include:
   - Blocking list (numbered)
   - `Nit:` list (optional)
   - Whether the PR is **ready for fix pass** (any blocking → yes, fix required)

## Stop

Hand off to **`sql-gym-pre-review-fix`** (implementer agent) when there are blocking items.

If **no blocking items**, say so explicitly and tell the **user** to run **`sql-gym-pre-review`** (or the fixer) for final tests/deslop/boxes—or run objective checks yourself only if the **user** asked you to complete the full pre-review in one flow.

Do **not** merge.

## References

- [sql-gym-pre-review](../sql-gym-pre-review/SKILL.md) — full loop
- [docs/WORKFLOW.md](../../../docs/WORKFLOW.md#pre-review-before-user-review)
