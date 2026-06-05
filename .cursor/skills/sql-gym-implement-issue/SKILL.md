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
5. Run tests/lint if configured. If they fail, **fix and re-run** before opening the PR (same branch).
6. Open or update a PR using [.github/pull_request_template.md](../../../.github/pull_request_template.md). Title: `TIM-NN: <summary>`. Description: *what*, *why*, test plan ([CL descriptions](https://github.com/google/eng-practices/blob/master/review/developer/cl-descriptions.md)).
7. Fill the template; leave **Agent pre-review** boxes **unchecked**. Prefer a **small, focused** PR ([small CLs](https://github.com/google/eng-practices/blob/master/review/developer/small-cls.md)).
8. Optional quick self-check: `code-reviewer` or a diff read against acceptance criteria. If you find **blocking** gaps, fix on the branch before handoff—do not rely on pre-review to discover obvious misses only.

## Stop

Do **not** mark the PR ready for **user** review. Do **not** check pre-review boxes or run the full pre-review loop in this skill—that is **`sql-gym-pre-review`**, which **iterates until checks pass**.

Tell the **user** to invoke **`sql-gym-pre-review`** when implementation is complete (or run it yourself in the same session if continuing).

## References

- [docs/WORKFLOW.md](../../../docs/WORKFLOW.md) — step 4
- Do not expand scope beyond the issue / PRD section without **user** approval
