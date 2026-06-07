---
name: sql-gym-start-issue
description: Start work on a Linear issue — read prd/, run local implement-from-prd, stop for user approval before any product code. Use when picking up TIM-NN or "start this issue".
---

# sql-gym: start issue

Planning only. Do **not** write application code in this skill.

## Inputs

Ask if missing:

- Linear issue id (e.g. `TIM-20`) or URL
- Optional: explicit `prd/` path and section

## Steps

1. Confirm [prd/README.md](../../../prd/README.md) names an **active phase** and the relevant `prd/` doc exists. If not, stop and tell the **user** to complete requirements first with local `write-prd`.
2. Load the Linear issue (Linear MCP). Read title, description, acceptance criteria, and linked `prd/…` reference.
3. Read the referenced `prd/` section (and surrounding context if needed).
4. Run local **`implement-from-prd`** on that PRD scope. Produce a milestone plan: files, order, risks.
5. Post the plan in chat (and optionally as a Linear comment). Ask the **user** to approve or adjust.

## Stop

**Stop here.** Do not edit product code until the **user** explicitly approves the plan.

Tell the **user** to invoke **`sql-gym-implement-issue`** (or say "approved, implement TIM-NN") when ready.

## References

- [docs/WORKFLOW.md](../../../docs/WORKFLOW.md) — steps 2–3
- [.cursor/rules/workflow.mdc](../../../.cursor/rules/workflow.mdc) — gates
