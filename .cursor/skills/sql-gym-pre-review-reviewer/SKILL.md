---
name: sql-gym-pre-review-reviewer
description: Independent agent pre-review (read-only) — alignment and code review findings only. Use in a new agent/session or Task subagent; do not commit. Pair with sql-gym-pre-review-fix for fixes.
---

# sql-gym: pre-review reviewer

**Review only.** Produce findings; do **not** edit the branch, commit, push, check PR boxes, or mark the PR ready for **user** review.

## Independence (required)

The reviewer must **not** be the same agent that implemented the PR.

| Situation | What to do |
|-----------|------------|
| **New agent / new chat / Cloud Agent handoff** | Preferred — pass PR URL, branch, `TIM-NN`, linked `prd/` section, and the approved implementation plan. |
| **Same session as implementer** | Launch a **Task** subagent (`code-reviewer` or `explore`, **readonly**) with only PR + plan + `prd/` context. Use **its** output as the review; do not self-review in the implementer voice. |
| **Cannot get independent review** | Escalate to the **user**; leave pre-review boxes unchecked. |

## Inputs

Ask if missing:

- PR URL or branch name
- Linear issue id (`TIM-NN`) and linked `prd/` section
- Approved phase implementation plan (from `implement-from-prd`)
- Pre-review pass number (default 1)

## Steps

1. Read the PR diff, description, and linked `prd/phase-*.md` section. Do **not** assume unstated intent from the implementer.
2. Local **`check-prd-alignment`** — missing AC, spec drift, deviations, and goal-fit opportunities.
   - If the linked PRD section is missing or ambiguous, escalate to the **user** and leave the `check-prd-alignment` PR box **unchecked**.
3. Superpowers **`code-reviewer`** vs the approved plan and [engineering.mdc](../../../.cursor/rules/engineering.mdc).
   - **If Superpowers is unavailable:** manually review the diff against the approved plan and `engineering.mdc` using available tools. Document this as "manual code review (Superpowers unavailable)" in findings. Leave the Superpowers PR box **unchecked**.
4. Review the diff against [docs/references/google-eng-practices.md](../../../docs/references/google-eng-practices.md). Use **`Nit:`** only for non-blocking items.
5. **Browser checks for user-facing behavior** — **case by case**, not a fixed mega-suite. No monolithic `test_workspace_browser.py` is required; the reviewer (or implementer) identifies **which flows this PR affects** and validates **those** in a real browser.
   - **Applies when** the diff touches user-facing surfaces: `templates/`, `static/js/`, `static/styles.css`, practice pages/APIs (`src/app/main.py`, `src/app/api/`, `src/app/workspace/`), or learner-visible copy/errors.
   - **N/A** only for docs-only, tooling-only, or strictly internal backend with no UI/client impact — state **N/A** in Tools, not “passed”.
   - **Workflow (each PR):**
     1. List **affected UX** from the diff (e.g. “grading modal dismiss”, “console scroll”, “answer SQL in details”, “prev/next nav”).
     2. **Run relevant committed tests** that already cover overlapping behavior (subset only — do not require the full list every time):
        ```bash
        uv run playwright install chromium   # once per environment if needed
        uv run pytest tests/test_grading_modal.py -v          # modal / submit / dismiss
        uv run pytest tests/test_workspace_console_scroll.py -v # run SQL + in-panel scroll
        ```
     3. **Validate PR-specific behavior** not covered above — use Playwright in the review session (script, `uv run python`, or control-ui harness): load workspace, perform the affected actions, assert layout/interaction. Record commands + outcome under **Tools** in findings (pass/fail metrics, screenshot path if taken).
     4. **Committed test optional:** add or extend a `tests/test_*.py` Playwright test when the behavior is a **regression we want to keep** (bugfix, easy-to-break interaction). One-off UI polish may be browser-validated in review only — note that in the PR test plan.
   - **Catalog of committed browser tests** (pick by relevance — read files before assuming coverage):
     | File | Covers |
     |------|--------|
     | `tests/test_grading_modal.py` | Modal hidden on load; submit opens modal; OK dismiss (desktop + iPhone); CSS `[hidden]` rule (static) |
     | `tests/test_workspace_console_scroll.py` | Large run SQL result; page height unchanged; scroll inside output console |
   - **Blocking** if:
     - A relevant committed test fails;
     - Affected UX was not validated in browser (committed test **or** documented ad-hoc Playwright check);
     - Claims like “scroll works” / “modal dismisses” rely only on static HTML/CSS string tests for interaction/layout.
   - In findings, include: **Affected UX** → **tests run** → **ad-hoc checks** → **pass/fail**.
6. **Triage** every item as **blocking** or **`Nit:`** and return the lists to the caller (orchestrator or **user**). Do not check PR boxes or mark ready for **user** review. Include:
   - Blocking list (numbered)
   - `Nit:` list (optional)
   - Which tools ran vs were unavailable (and manual fallback used instead)

## Stop

Return findings to **`sql-gym-pre-review`** (preferred) or hand off to **`sql-gym-pre-review-fix`** when invoked standalone and there are blocking items.

If **no blocking items**, report that to the caller; full checklist and handoff are handled by **`sql-gym-pre-review`**.

Do **not** merge (per [workflow.mdc](../../rules/workflow.mdc) gates).

## References

- [sql-gym-pre-review](../sql-gym-pre-review/SKILL.md) — orchestrator and handoff
- [sql-gym-pre-review-fix](../sql-gym-pre-review-fix/SKILL.md) — blocking fixes
- [.cursor/rules/workflow.mdc](../../../.cursor/rules/workflow.mdc) — gate only
