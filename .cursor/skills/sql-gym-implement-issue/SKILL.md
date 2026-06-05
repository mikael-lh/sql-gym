---
name: sql-gym-implement-issue
description: Implement an approved plan for a Linear issue — branch, code to acceptance criteria, draft PR. Use after sql-gym-start-issue when the user approved the plan.
---

# sql-gym: implement issue

Coding only. Requires an **approved** plan from `implement-from-prd` (via **sql-gym-start-issue** or equivalent).

## Inputs

Ask if missing:

- Linear issue id (e.g. `TIM-20`)
- Confirmation that the **user** approved the implementation plan

If there is no approved plan, run **sql-gym-start-issue** first and stop.

## Steps

1. Re-read the Linear issue and linked `prd/` acceptance criteria.
2. Create a branch: `cursor/<short-desc>-e2d9` or `feature/tim-NN-<short-desc>`.
3. Implement **only** the acceptance criteria from the approved plan. Follow [.cursor/rules/engineering.mdc](../../../.cursor/rules/engineering.mdc).
4. Optional: Superpowers **`executing-plans`** for step order; TDD skills when tests exist.
5. Run tests/lint if configured; otherwise note in the PR what was run manually.
6. Open or update a PR using [.github/pull_request_template.md](../../../.github/pull_request_template.md). Title: `TIM-NN: <summary>`.
7. Fill the template; leave agent pre-review boxes unchecked unless already done.

## Stop

Do **not** mark the PR ready for **user** review. Do **not** run full pre-review in this skill.

Tell the **user** to invoke **`sql-gym-pre-review`** when implementation is complete.

## References

- [docs/WORKFLOW.md](../../../docs/WORKFLOW.md) — step 4
- Do not expand scope beyond the issue / PRD section without **user** approval
