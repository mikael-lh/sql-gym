---
name: sql-gym-pre-review
description: Run agent pre-review before user review — check-prd-alignment, code-reviewer, deslop, tests. Use when a PR is implemented and ready for checklist pass.
---

# sql-gym: pre-review

Run before marking a PR ready for **user** review. Does **not** replace **user** judgment on product/architecture.

## Inputs

Ask if missing:

- PR URL or branch name
- Linear issue id (`TIM-NN`) and linked `prd/` section

## Steps

1. Identify the PR diff and linked `prd/phase-*.md` section (from issue or PR description).
2. ChatPRD **`check-prd-alignment`** — record gaps, missing AC, and deviations in the PR description.
3. Superpowers **`code-reviewer`** against the approved implementation plan and [engineering.mdc](../../../.cursor/rules/engineering.mdc).
4. Review the diff against [docs/references/google-eng-practices.md](../../../docs/references/google-eng-practices.md) (design, functionality, complexity, tests, naming, comments, documentation, context). Record findings in the PR; use **`Nit:`** for non-blocking items.
5. cursor-team-kit **`deslop`** on changed code files (or mark N/A if docs-only).
6. Run tests/lint; if CI is not configured, state what was run manually in the PR.
7. Update the PR description with: summary, risks, test plan, alignment notes, PRD deviations, and notable **Nit:** items.
8. Check all boxes under **Agent pre-review** in the PR template.
9. Mark the PR ready for **user** review (or tell the **user** it is ready).

## Stop

Do not merge. The **user** performs final review and merge.

## References

- [docs/WORKFLOW.md](../../../docs/WORKFLOW.md) — [Pre-review before user review](../../../docs/WORKFLOW.md#pre-review-before-user-review)
- [.cursor/rules/workflow.mdc](../../../.cursor/rules/workflow.mdc)
