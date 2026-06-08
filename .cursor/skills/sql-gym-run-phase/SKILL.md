---
name: sql-gym-run-phase
description: Use when the user asks an agent to autonomously execute an approved sql-gym phase plan.
---

# sql-gym: run phase

Orchestrates an already-approved phase implementation plan across its Linear child issues. Do not use this to define product scope or create a plan.

## Inputs

Ask if missing:

- Phase name or approved implementation plan path, e.g. `docs/phase-1-implementation-plan.md`
- Ordered Linear child issues to run, if not listed in the plan
- Confirmation that the **user** authorizes autonomous execution for this phase
- Whether implementation PRs may be merged autonomously
- Whether `update-prd` PRs may be merged autonomously
- Merge method: `squash`, `merge`, or `rebase`

Stop if merge authorization scope or merge method is unclear.

## Steps

1. Read `prd/README.md`, the phase PRD, and the approved phase implementation plan.
2. Derive the ordered issue list from the approved plan and Linear. Before starting each issue:
   - Pull `main`.
   - Check whether the issue is already done or already has a merged PR; skip completed issues and note the reason.
   - Check for open implementation or PRD-update PRs from a previous paused run; resume or resolve them before starting a new issue.
3. For each planned Linear child issue, in approved order:
   - Run **`sql-gym-implement-issue`** for that issue.
   - Run **`sql-gym-pre-review`** until there are no blocking findings.
   - Confirm final validation is green and the PR is mergeable.
   - If implementation PR merge is authorized, merge the PR with GitHub MCP `merge_pull_request` using the approved merge method. Otherwise stop for user merge.
   - Pull `main`.
   - Always run local **`update-prd`** assessment. If no PRD update is needed, record that in the run summary. If a PRD update is needed, create its PR; merge it only when `update-prd` PR merge is authorized, otherwise stop for user merge.
   - Pull `main` again after any authorized `update-prd` PR merge.
   - Close or update the Linear issue after the implementation PR is merged and PRD reality is updated or explicitly assessed as unchanged.
4. Continue to the next issue.

## Escalate and stop

Stop for the **user** when:

- Linear, PRD, and approved plan conflict.
- A change would expand product scope beyond the approved issue.
- Product behavior is ambiguous.
- Required checks fail and cannot be fixed after reasonable remediation.
- Independent pre-review reports blocking findings that require product or architecture decisions.
- GitHub MCP merge fails because of permissions, branch protection, or failing checks.
- Merge authorization does not cover the PR type that needs merging.

## Guardrails

- One implementation issue per PR.
- Do not skip `sql-gym-pre-review`.
- Do not merge with unresolved blocking findings.
- Do not mark a Linear issue done before its implementation PR is merged and PRD reality is updated when needed.
- Do not use `gh` for write operations; use GitHub MCP tools for PR create/update/merge.
- Keep a concise run summary in the final response: completed issues, skipped issues, PRs merged, PRD updates, and any stops.
