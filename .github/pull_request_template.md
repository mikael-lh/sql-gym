## Linear

- Issue: TIM-___ (or N/A for process-only PRs)

## Agent pre-review (before user review)

Check only after **`sql-gym-pre-review`** passes: independent **reviewer** agent found no blocking items, **fixer** addressed prior blocking findings, tests/lint green—do not check boxes to hand off a failing PR.

- [ ] `check-prd-alignment` — no blocking gaps (or approved deviation noted)
- [ ] Superpowers `code-reviewer` (or N/A — docs-only) — blocking feedback addressed
- [ ] Reviewed against [google-eng-practices](docs/references/google-eng-practices.md) (or N/A — docs-only) — blocking items fixed
- [ ] cursor-team-kit `deslop` (or N/A — docs-only)
- [ ] Tests/lint run (or **CI not configured yet** — manual checks: ___)
- [ ] Browser checks for user-facing behavior (or N/A — no UI/client impact) — affected flows listed; relevant Playwright tests + ad-hoc browser validation recorded in PR/review
- [ ] Layout/responsive CSS (or N/A — no `templates/` / `static/styles.css` layout change) — [ui-layout-review.md](docs/ui-layout-review.md): desktop + mobile viewport tests; all controls in group asserted; pre-review not skipped

## PRD

- [ ] N/A — process/docs only
- [ ] Matches `prd/…` section: ___

## Acceptance criteria

- [ ] …

## Deviations from PRD

<!-- none / explain -->

## Summary & risks

<!-- what changed, what could go wrong -->

## Test plan

- [ ] …
