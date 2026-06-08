---
name: update-prd
description: Update a local PRD to reflect what was actually built, including decisions, deviations, deferred work, and follow-up requirements.
---

# Update local PRD

## Trigger

The user has finished implementation or merged a change and wants the PRD to reflect reality.

## Source of truth

Committed markdown under `prd/` (per [workflow.mdc](../../rules/workflow.mdc) gates).

## Workflow

1. Identify the PRD to update.
   - Ask for the PRD path or section if missing.
   - Check the PR, branch, commits, or Linear issue for a linked `prd/...` reference.
2. Read the current PRD.
   - Preserve its structure where possible.
   - Note requirements, acceptance criteria, open questions, and future work.
3. Analyze what changed.
   - Review the diff against the base branch.
   - Read relevant tests, docs, PR description, and implementation notes.
   - Identify what was built, deferred, removed, or changed.
4. Compare implementation to the PRD.
   - Requirements implemented as specified.
   - Approved deviations and their rationale.
   - Deferred or cut scope.
   - New edge cases or constraints discovered during implementation.
5. Update the PRD.
   - Add a concise **What was actually built** section when useful.
   - Mark completed requirements only when evidence supports completion.
   - Move deferred items to **Future work**.
   - Resolve or update open questions that were answered by implementation.
   - Add dated notes only when the repo's existing PRD style uses them.
6. Update `prd/README.md` if status, active phase, or index entries changed.
7. Commit the PRD update and open or update a draft PR.

## Guardrails

- Preserve product history; do not rewrite the PRD to hide deviations.
- Be factual and concise.
- Do not expand scope while documenting what shipped.
- Do not mark uncertain behavior as complete.
- Keep future work explicit so it is not lost.

## Output

- Updated local PRD.
- Updated `prd/README.md` if needed.
- Summary of completed, deviated, and deferred items.
- Any follow-up issues or PRD sections the user should create.
