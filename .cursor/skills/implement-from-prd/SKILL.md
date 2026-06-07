---
name: implement-from-prd
description: Generate a scoped implementation plan from a local PRD. Use before building a phase or feature; stops for user approval before code changes.
---

# Implement from local PRD

## Trigger

The user wants to plan implementation for an approved local PRD or a specific PRD section.

## Source of truth

Use committed files under `prd/` as the product source of truth. Do not fetch or require ChatPRD cloud documents.

## Workflow

1. Identify the PRD scope.
   - Ask for the PRD path or section if missing.
   - If a Linear issue is provided, read the issue and follow its linked `prd/...` reference.
   - Read `prd/README.md` to confirm the relevant phase is active when implementation is requested.
2. Read the PRD.
   - Extract goals, non-goals, requirements, acceptance criteria, edge cases, and open questions.
   - Stop if required product decisions are still open and block implementation planning.
3. Explore the codebase.
   - Inspect existing app structure, data models, APIs, routes, tests, docs, and package/tooling files.
   - If application code does not exist yet, identify the scaffolding decisions that must be made.
4. Produce an implementation plan.
   - Break the PRD into ordered milestones, each small enough for a focused PR.
   - For each milestone, list files to create or modify, key implementation details, acceptance criteria covered, tests/checks, and risks.
   - Map every PRD requirement and acceptance criterion to at least one milestone.
   - Call out out-of-scope items explicitly so they are not accidentally implemented.
5. Check the plan against engineering principles.
   - Read `docs/references/google-eng-practices.md` and `.cursor/rules/engineering.mdc`.
   - Confirm the plan has small focused changes, design fit, low complexity, clear tests, clear naming, and documentation updates.
   - Revise the plan before presenting it if the check finds blocking gaps.
   - Call out any remaining non-blocking trade-offs or risks for user review.
6. Present the plan for user review.
   - Ask the user to approve or adjust the plan.
   - Do not edit application code until the user approves the plan.

## Guardrails

- Planning only until the user explicitly approves.
- Do not expand beyond the PRD section or Linear issue scope.
- Do not hide ambiguous requirements; list them as blockers or risks.
- Prefer repo conventions and existing architecture over new patterns.
- Keep implementation milestones reviewable and independently testable.

## Output

- Ordered milestone plan.
- File-level change list per milestone.
- Requirement coverage mapping.
- Engineering-principles check results.
- Risks, unknowns, and blocked decisions.
- Clear approval request before implementation starts.
