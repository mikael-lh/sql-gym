---
name: sql-gym-implement-issue
description: Implement a Linear issue after a phase PRD and implementation plan are approved.
---

# sql-gym: implement issue

Coding only. Requires an active phase PRD and an **approved phase implementation plan** from local `implement-from-prd`.

## Inputs

Ask if missing:

- Linear issue id (e.g. `TIM-20`)
- Confirmation that the **user** approved the phase implementation plan

If there is no approved phase implementation plan, stop and run local **`implement-from-prd`** before writing application code.

## Steps

1. Confirm [prd/README.md](../../../prd/README.md) names an **active phase**, the relevant `prd/` doc exists, and the approved phase implementation plan exists.
2. Load the Linear issue (Linear MCP). Read title, description, acceptance criteria, linked `prd/…` reference, parent issue, and branch name if present.
3. Read the linked `prd/` section and the matching approved implementation plan milestone for this issue.
4. Compare the Linear issue, PRD section, and implementation plan milestone:
   - If they conflict or the issue expands scope beyond the approved plan, stop and ask the **user** to update the issue, PRD, or plan.
   - If the issue is not covered by the approved plan, stop and ask the **user** to run local `implement-from-prd` for the new scope.
5. Create a branch using the `cursor/<short-desc>-<suffix>` convention (the cloud agent template supplies the suffix for the active session, e.g. `cursor/tim-42-parser-7a6a`).
6. Implement **only** the acceptance criteria for this Linear issue and its approved plan milestone. Follow [.cursor/rules/engineering.mdc](../../../.cursor/rules/engineering.mdc).
7. Optional: Superpowers **`executing-plans`** for step order; TDD skills when tests exist.
8. Run tests/lint if configured. If they fail, **fix and re-run** before opening the PR (same branch).
9. Open or update a PR using [.github/pull_request_template.md](../../../.github/pull_request_template.md). Title: `TIM-NN: <summary>`. Description: *what*, *why*, test plan ([CL descriptions](https://github.com/google/eng-practices/blob/master/review/developer/cl-descriptions.md)).
10. Fill the template; leave **Agent pre-review** boxes **unchecked**. Prefer a **small, focused** PR ([small CLs](https://github.com/google/eng-practices/blob/master/review/developer/small-cls.md)).
11. Optional quick self-check: `code-reviewer` or a diff read against acceptance criteria. If you find **blocking** gaps, fix on the branch before handoff—do not rely on pre-review to discover obvious misses only.

## Stop

Do **not** mark the PR ready for **user** review. Do **not** check pre-review boxes or run the full pre-review loop in this skill—that is **`sql-gym-pre-review`**, which **iterates until checks pass**.

Tell the **user** to run **`sql-gym-pre-review`** when implementation is complete (same or new Cursor chat / Cloud Agent).

## References

- [docs/WORKFLOW.md § End-to-end flow](../../../docs/WORKFLOW.md#end-to-end-flow)
- Do not expand scope beyond the issue / PRD section without **user** approval
