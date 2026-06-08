---
name: check-prd-alignment
description: Compare current changes against a local PRD to find coverage gaps, deviations, and goal-aligned improvement opportunities.
---

# Check local PRD alignment

## Trigger

The user wants to verify that implementation changes match the relevant product requirements before review or merge.

## Workflow

1. Identify the comparison target.
   - Determine the base branch, usually `main`.
   - Review `git diff` against the base branch, plus relevant commits and PR description if available.
2. Identify the PRD.
   - Ask for the PRD path or section if missing.
   - Check the Linear issue or PR description for a linked `prd/...` reference.
   - Read `prd/README.md` and the relevant PRD section.
3. Extract the PRD expectations.
   - Goals
   - Non-goals and out-of-scope items
   - Requirements
   - Acceptance criteria
   - Edge cases and error states
   - Open questions that affect the implementation
4. Compare each requirement against the diff.
   - **Covered:** implemented and matching the PRD.
   - **Partial:** started but incomplete or missing edge cases.
   - **Missing:** not addressed in current changes.
   - **Deviated:** implemented differently than specified.
   - **Out of scope:** explicitly deferred by the PRD and not required.
5. Review goal fit.
   - Add **Opportunity** items only when they are concrete, actionable, and tied to a PRD goal.
   - Distinguish optional improvements from blocking requirement gaps.
6. Report findings.
   - Cite specific files and line ranges when possible.
   - Mark each finding as blocking or non-blocking.
   - Note approved deviations separately from accidental deviations.

## Guardrails

- Do not invent requirements beyond the PRD.
- Do not flag out-of-scope items as missing.
- Be specific and evidence-based.
- Keep opportunity items grounded in stated goals.
- If the PRD is too ambiguous to judge alignment, escalate to the user instead of guessing.

## Output

- Requirement coverage table or list.
- Blocking gaps, partials, and deviations.
- Non-blocking **Opportunity** items tied to goals.
- Overall alignment summary.
- Recommended next steps.
