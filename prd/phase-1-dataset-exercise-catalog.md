# Phase 1 dataset and exercise catalog PRD

## Status

Complete (2026-06-08). Shipped via TIM-25, TIM-27, TIM-29, TIM-28, and TIM-26 ([TIM-24](https://linear.app/times-api/issue/TIM-24/phase-1-or-dataset-and-exercise-catalog) epic).

## Source context

This phase follows the SQL Gym product vision in `prd/00-product-vision.md`, especially the core loop steps where a learner picks a dataset, picks difficulty, chooses timed or untimed practice, and completes a SQL exercise.

Phase 0 in `prd/phase-0-product-scaffolding.md` established the FastAPI scaffold, server-rendered pages, Pydantic domain model boundaries, a Times Archive dataset placeholder, a single placeholder exercise, static demo progress, and baseline validation commands. It intentionally did not implement a real catalog, SQL execution, grading, AI feedback, authentication, or durable progress storage.

Implementation context at ship:

- `src/app/domain/` — catalog models (`datasets.py`, `exercises.py`, `catalog.py`) with production-ready `TIMES_ARCHIVE_CATALOG_DATASET`.
- `src/app/catalog/` — JSON-backed Times exercise loader and `TIMES_ARCHIVE_CATALOG` (50 entries).
- `src/app/practice.py` — catalog browsing filters and exercise preview lookup helpers.
- `templates/practice.html` — catalog browsing inside `/practice` with filters and exercise cards.
- `templates/practice_exercise.html` — exercise preview at `/practice/{dataset_id}/{exercise_id}`.
- `templates/404.html` — user-friendly not-found responses for unknown preview routes.
- `src/app/fixtures/times/archive_articles_demo.json` — small schema-aligned article row fixture (still demo-sized).
- Tests in `tests/test_app.py`, `tests/test_domain.py`, and `tests/test_developer_workflow.py` guard catalog behavior, placeholder honesty, and docs.

## Problem

SQL Gym currently shows the intended practice flow but does not yet have a real dataset or exercise catalog. Learners can see a Times demo placeholder and a sample SQL prompt, but they cannot browse catalog entries, understand which exercises are available, or choose a catalog-backed practice item.

Future implementation work also needs a structured source of truth for datasets and exercises so catalog additions do not require rewriting the product shell or duplicating metadata across templates.

## Goals

- Turn the Phase 0 placeholders into a small, honest catalog surface for datasets and exercises.
- Preserve the Times Archive as the first production catalog dataset while keeping provenance labels clear.
- Define catalog metadata that supports dataset, difficulty, mode, dialect, concept tags, estimated time, learning objectives, and exercise selection.
- Let learners browse available catalog entries only when they explicitly choose to practice, without implying SQL execution or grading is complete.
- Keep the catalog replaceable so future SQL execution, grading, progress, and production Times refresh work can build on it.
- Keep Phase 1 focused enough for small implementation PRs with clear tests.

## Non-goals

- Executing submitted SQL.
- Computing exact query results or comparing expected result sets.
- AI grading, explanations, or partial credit.
- User authentication, accounts, or personalization.
- Durable progress, attempt history, or database-backed state.
- Scheduled Times refresh automation beyond the initial production-ready catalog data.
- Exercise authoring tooling for non-developers.
- Supporting arbitrary user-uploaded datasets.
- Full timed-mode scoring or interview-mode behavior.

## Users and use cases

### Learner

As a learner, I want to browse available datasets and exercises when I choose to practice so I can choose a SQL practice item that matches my level.

As a learner, I want clear labels for demo data and placeholders so I understand what works today and what is still future work.

### Future implementer

As a future implementer, I want datasets and exercises represented as catalog data so I can add SQL execution, grading, progress, and more content without reworking the shell.

### Reviewer

As a reviewer, I want catalog entries and UI copy to make non-working behavior explicit, so Phase 1 does not overclaim SQL execution, grading, persistence, auth, or AI capabilities.

## Requirements

### R1. Dataset catalog foundation

The app must have a structured catalog source for available datasets.

Acceptance criteria:

- The catalog includes the Times Archive dataset as the first production-ready dataset.
- Each dataset entry includes stable id, display name, short description, provenance/source metadata, schema reference, fixture or data reference, and demo/production status.
- Dataset provenance continues to reference `times-api` and clearly distinguishes production-ready catalog data from any future sample-only data.
- The catalog can represent future datasets without changing page templates directly.

### R2. Exercise catalog foundation

The app must have a structured catalog source for SQL exercises tied to datasets.

Acceptance criteria:

- The catalog includes 50 initial exercise entries for the Times Archive dataset.
- Each exercise entry includes stable id, dataset id, title, prompt, difficulty, mode, target SQL dialect, concept tags, estimated time, learning objectives, and placeholder/availability status.
- Exercise detail data reserves structured fields for future expected results while keeping exact grading out of scope in Phase 1.
- Exercise entries use PostgreSQL as the target dialect unless a later approved PRD changes dialect support.
- Exercise entries can be grouped or filtered by dataset, difficulty, and practice mode.
- Invalid catalog data, such as an exercise referencing an unknown dataset or unsupported difficulty/mode/dialect, is rejected by tests or validation.

### R3. Catalog browse and selection surface

The practice flow must let learners browse catalog-backed datasets and exercises when they explicitly choose to practice.

Acceptance criteria:

- A learner can see available dataset catalog entries from `/practice` or a practice-specific route reached from `/practice`.
- A learner can see exercise catalog entries with title, prompt summary, difficulty, mode, and dialect.
- A learner can choose or navigate to a catalog-backed exercise detail or practice preview.
- Catalog-backed selection replaces hard-coded single-placeholder assumptions where appropriate.
- SQL editor, grading feedback, and progress areas remain visibly placeholder-only if shown in the selected exercise flow.
- Phase 1 does not add a standalone catalog route; users encounter catalog browsing only in the practice flow.

### R4. Placeholder honesty and boundaries

The catalog must not imply that unimplemented product capabilities work.

Acceptance criteria:

- The UI and docs clearly state that SQL execution is not available in Phase 1.
- The UI and docs clearly state that grading is not available in Phase 1.
- Times data provenance is visible and production-ready catalog entries are not labeled as demo-only.
- Sample SQL is hidden behind a hint or placeholder pattern by default and is framed as illustrative content, not as an executed answer.
- No account, persistence, AI, or durable progress requirement is introduced.

### R5. Developer and reviewer workflow

Catalog work must remain easy to validate and extend.

Acceptance criteria:

- Tests cover dataset catalog metadata, exercise catalog metadata, invalid catalog references, and catalog-backed page rendering.
- README or linked developer docs are updated if setup, validation, or placeholder behavior changes.
- `./scripts/validate-env.sh` remains the full local validation command.
- Future phases can replace demo fixture data or add execution/grading without rewriting the catalog-facing shell.

## Edge cases and error states

- Empty catalog: the UI should show a clear empty-state message rather than failing.
- Unknown dataset id: exercise validation or routing should reject it.
- Unknown exercise id: the app should show a clear not-found response or equivalent error state.
- Unsupported difficulty, mode, or SQL dialect: catalog validation should reject the entry.
- Missing provenance or schema reference: dataset validation should reject the entry.
- Production-ready Times data shown in UI: the page must keep source and schema provenance visible.
- Timed mode selected before timed behavior exists: the page must label timed behavior as unavailable or future work.
- Unknown dataset or exercise detail route: the app should return a user-friendly 404 response.
- Catalog filters with no matches: the practice flow should show an inline empty state rather than a 404.

## Out of scope for Phase 1

- Real SQL query execution.
- Exact-result grading and expected result comparison.
- AI grading or explanations.
- Durable progress tracking.
- Authentication or user-specific catalog state.
- Scheduled Times refresh process or ingestion automation beyond the initial production-ready catalog data.
- Broad responsive design polish beyond clear catalog usability.
- Non-developer exercise authoring workflows.

## Success signals

Phase 1 is successful when a reviewer can:

- See a catalog-backed dataset and 50 initial Times exercise entries in the practice flow.
- Identify catalog provenance and which exercise capabilities are still placeholder-backed.
- Select or navigate to an exercise from the practice flow without SQL execution or grading being implied.
- Add or review a catalog entry through structured data and focused tests.
- Run the documented validation commands successfully.

## Resolved product decisions

- Phase 1 includes 50 initial Times exercises.
- Catalog browsing is integrated into the practice flow; there is no standalone catalog route in Phase 1.
- Exercise entries include concept tags, estimated time, and learning objectives.
- Sample SQL is hidden behind a hint or placeholder pattern by default.
- Exercise details reserve structured fields for future expected results, but exact grading stays out of scope.
- Unknown dataset or exercise detail routes return a user-friendly 404 response; empty filter results use an inline empty state.
- Times source and schema are production-ready for Phase 1 catalog use, so the initial Times catalog can be production catalog data rather than demo-only data.

## What was actually built

- Catalog domain model with validation (`TIM-25`, PR #56).
- 50 Times Archive exercises in structured JSON with loader and tests (`TIM-27`, PR #57).
- Practice-flow catalog browsing with dataset/difficulty/mode filters (`TIM-29`, PR #58).
- Exercise preview routes, hint/sample SQL disclosure, and 404 handling (`TIM-28`, PR #59).
- README and developer workflow doc guards for Phase 1 boundaries (`TIM-26`, PR #60).

## Deviations and deferred work

- **Article row data:** catalog exercise metadata is production-ready, but article rows still come from the two-row demo fixture. A later phase should wire full Times article data or document the refresh path.
- **Home page:** `/` still presents Phase 0 shell copy; catalog work is centered on `/practice`.
- **Exercise availability:** `availability_status` replaced a separate `is_placeholder` boolean on `Exercise` during implementation.
- **Still out of scope (unchanged):** SQL execution, grading, auth, durable progress, AI feedback, timed scoring, and non-developer authoring tooling.
