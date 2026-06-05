---
name: sql-gym-pre-review
description: Run agent pre-review before user review — check-prd-alignment, code-reviewer, deslop, tests. Iterate on the branch until checks pass; only then check PR boxes and hand off to the user.
---

# sql-gym: pre-review

Run before marking a PR ready for **user** review. Does **not** replace **user** judgment on product/architecture.

**Default behavior:** **iterate** on the same branch until pre-review **passes**. Do **not** check template boxes or ask for **user** review while blocking issues remain.

## Inputs

Ask if missing:

- PR URL or branch name
- Linear issue id (`TIM-NN`) and linked `prd/` section

## Blocking vs non-blocking

| Kind | Examples | Action |
|------|----------|--------|
| **Blocking** | Missing acceptance criteria, spec drift without approved deviation, failed tests/lint, `code-reviewer` must-fix, eng-practices issues (not `Nit:`), fixable `deslop` findings | **Fix** on the branch, commit, push, re-run checks |
| **Non-blocking** | Style nits, optional polish | Prefix with **`Nit:`** in the PR; may ship without fixing |

## Iteration loop

Repeat until there are **no blocking findings** or you must **escalate** (see Stop):

1. Identify the PR diff and linked `prd/phase-*.md` section (from issue or PR description).
2. ChatPRD **`check-prd-alignment`** — record gaps, missing AC, and deviations in the PR description.
3. Superpowers **`code-reviewer`** against the approved implementation plan and [engineering.mdc](../../../.cursor/rules/engineering.mdc).
4. Review the diff against [docs/references/google-eng-practices.md](../../../docs/references/google-eng-practices.md). Record findings; use **`Nit:`** for non-blocking items only.
5. cursor-team-kit **`deslop`** on changed code files (or mark N/A if docs-only).
6. Run tests/lint; if CI is not configured, run equivalent commands manually.
7. **Triage:** list blocking vs `Nit:` items in the PR (or a short comment on the PR).
8. **If any blocking item remains:** implement fixes on the **same branch**, commit, push, update the PR description, then **go back to step 1**. Do **not** check pre-review boxes yet.
9. **If no blocking items:** update the PR description (summary, risks, test plan, alignment notes, PRD deviations, `Nit:` list). Check all boxes under **Agent pre-review**. Mark the PR ready for **user** review (or tell the **user** it is ready).

Track iteration in the PR when helpful (e.g. “Pre-review pass 2 — fixed AC gap in …”).

## Escalate to the user (do not fake pass)

Stop iterating and ask the **user** when:

- A **product or architecture** decision is required (scope change, intentional PRD deviation).
- Checks cannot run (missing credentials, plugin unavailable) and you cannot complete them another way.
- You are stuck after **multiple** fix cycles on the same class of issue — summarize what you tried and what you need.

While escalated: leave pre-review boxes **unchecked** and the PR **draft** unless the **user** says otherwise.

## Stop

Do not merge. The **user** performs final review and merge.

## References

- [docs/WORKFLOW.md](../../../docs/WORKFLOW.md) — [Pre-review before user review](../../../docs/WORKFLOW.md#pre-review-before-user-review)
- [.cursor/rules/workflow.mdc](../../../.cursor/rules/workflow.mdc)
