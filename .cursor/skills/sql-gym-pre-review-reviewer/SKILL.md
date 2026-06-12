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
5. **Playwright browser checks for user-facing behavior** — required when the PR changes anything learners see or interact with in the browser (not scrolling-only):
   - **Applies when** the diff touches user-facing surfaces, including: `templates/`, `static/js/`, `static/styles.css`, practice page/API routes (`src/app/main.py` pages, `src/app/api/`, `src/app/workspace/`), or learner-visible copy/errors wired to the UI.
   - **N/A** only for docs-only, tooling-only, or strictly internal backend changes with no UI or client-contract impact — state **N/A** in Tools, not “passed”.
   - **Run all existing workspace Playwright tests** (after `uv sync`):
     ```bash
     uv run playwright install chromium
     uv run pytest tests/test_grading_modal.py tests/test_workspace_console_scroll.py -v
     ```
   - **What those tests cover today** (read the files — do not assume broader coverage):
     | File | Browser? | Verifies |
     |------|----------|----------|
     | `tests/test_grading_modal.py` | Partial | CSS `[hidden]` rule (static); modal **not visible on load**; empty submit opens modal; **OK dismisses** on desktop click and iPhone tap |
     | `tests/test_workspace_console_scroll.py` | Yes | **Run SQL** with a large result; **page height unchanged**; results **scroll inside** the output console panel |
     | *(no other Playwright workspace tests yet)* | — | Run SQL display, prev/next nav, drawer, filters, grading pass/fail, timer, clear progress, answer SQL, etc. are **not** automated |
   - **Blocking** if:
     - Existing Playwright tests fail or Chromium cannot be installed;
     - The PR changes user-facing behavior but adds **no** Playwright coverage when a test should exist for that flow (new test in `tests/test_*.py` using Playwright, or extend an existing browser test);
     - The PR only relies on static/HTML assertions for behavior that requires a real browser (clicks, scroll, layout).
   - Reviewer should name the **changed UX** in findings and state whether it is covered by an existing browser test, a new test in the PR, or why N/A.
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
