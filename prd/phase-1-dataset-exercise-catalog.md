# Phase 1 dataset and exercise catalog PRD

## Status

Draft for approval. Do not mark Phase 1 active, create implementation issues, or write application code until the user approves this PRD and a scoped implementation plan.

## Source context

This phase follows the SQL Gym product vision in `prd/00-product-vision.md`, especially the core loop steps where a learner picks a dataset, picks difficulty, chooses timed or untimed practice, and completes a SQL exercise.

Phase 0 in `prd/phase-0-product-scaffolding.md` established the FastAPI scaffold, server-rendered pages, Pydantic domain model boundaries, a Times Archive demo dataset placeholder, a single placeholder exercise, static demo progress, and baseline validation commands. It intentionally did not implement a real catalog, SQL execution, grading, AI feedback, authentication, or durable progress storage.

Current implementation context:

- `src/app/domain/datasets.py` defines `Dataset` and `DatasetProvenance`, with one `TIMES_ARCHIVE_DEMO_DATASET`.
- `src/app/domain/exercises.py` defines `Exercise`, difficulty/mode/dialect literals, selection options, and one `TIMES_ARCHIVE_PLACEHOLDER_EXERCISE`.
- `src/app/practice.py` assembles a single practice-page context from domain constants.
- `templates/practice.html` shows disabled placeholder controls for dataset, difficulty, mode, editor, grading, and progress.
- `src/app/fixtures/times/archive_articles_demo.json` contains tiny Times demo rows with provenance metadata; it is not loaded as a real production dataset.
- Existing tests in `tests/test_app.py`, `tests/test_domain.py`, and `tests/test_developer_workflow.py` guard placeholder copy, domain validation, Times provenance, and developer workflow documentation.

## Problem

SQL Gym currently shows the intended practice flow but does not yet have a real dataset or exercise catalog. Learners can see a Times demo placeholder and a sample SQL prompt, but they cannot browse catalog entries, understand which exercises are available, or choose a catalog-backed practice item.

Future implementation work also needs a structured source of truth for datasets and exercises so catalog additions do not require rewriting the product shell or duplicating metadata across templates.

## Goals

- Turn the Phase 0 placeholders into a small, honest catalog surface for datasets and exercises.
- Preserve the Times Archive as the first intended dataset while keeping demo/provenance labels clear.
- Define catalog metadata that supports dataset, difficulty, mode, dialect, and exercise selection.
- Let learners browse available catalog entries and select an exercise without implying SQL execution or grading is complete.
- Keep the catalog replaceable so future SQL execution, grading, progress, and production Times refresh work can build on it.
- Keep Phase 1 focused enough for small implementation PRs with clear tests.

## Non-goals

- Executing submitted SQL.
- Computing exact query results or comparing expected result sets.
- AI grading, explanations, or partial credit.
- User authentication, accounts, or personalization.
- Durable progress, attempt history, or database-backed state.
- Production Times refresh automation.
- Exercise authoring tooling for non-developers.
- Supporting arbitrary user-uploaded datasets.
- Full timed-mode scoring or interview-mode behavior.

## Users and use cases

### Learner

As a learner, I want to browse available datasets and exercises so I can choose a SQL practice item that matches my level.

As a learner, I want clear labels for demo data and placeholders so I understand what works today and what is still future work.

### Future implementer

As a future implementer, I want datasets and exercises represented as catalog data so I can add SQL execution, grading, progress, and more content without reworking the shell.

### Reviewer

As a reviewer, I want catalog entries and UI copy to make non-working behavior explicit, so Phase 1 does not overclaim SQL execution, grading, persistence, auth, or AI capabilities.

## Requirements

### R1. Dataset catalog foundation

The app must have a structured catalog source for available datasets.

Acceptance criteria:

- The catalog includes the Times Archive demo dataset as the first dataset.
- Each dataset entry includes stable id, display name, short description, provenance/source metadata, schema reference, fixture or data reference, and demo/production status.
- Dataset provenance continues to reference `times-api` and clearly states when data is demo-only.
- The catalog can represent future datasets without changing page templates directly.

### R2. Exercise catalog foundation

The app must have a structured catalog source for SQL exercises tied to datasets.

Acceptance criteria:

- The catalog includes multiple exercise entries for the Times Archive demo dataset.
- Each exercise entry includes stable id, dataset id, title, prompt, difficulty, mode, target SQL dialect, and placeholder/availability status.
- Exercise entries use PostgreSQL as the target dialect unless a later approved PRD changes dialect support.
- Exercise entries can be grouped or filtered by dataset, difficulty, and practice mode.
- Invalid catalog data, such as an exercise referencing an unknown dataset or unsupported difficulty/mode/dialect, is rejected by tests or validation.

### R3. Catalog browse and selection surface

The UI must let learners browse catalog-backed datasets and exercises.

Acceptance criteria:

- A learner can see the available dataset catalog entry or entries from a page in the app.
- A learner can see exercise catalog entries with title, prompt summary, difficulty, mode, and dialect.
- A learner can choose or navigate to a catalog-backed exercise detail or practice preview.
- Catalog-backed selection replaces hard-coded single-placeholder assumptions where appropriate.
- SQL editor, grading feedback, and progress areas remain visibly placeholder-only if shown in the selected exercise flow.

### R4. Placeholder honesty and boundaries

The catalog must not imply that unimplemented product capabilities work.

Acceptance criteria:

- The UI and docs clearly state that SQL execution is not available in Phase 1.
- The UI and docs clearly state that grading is not available in Phase 1.
- Demo Times data is labeled as sample-only and not final production Times data.
- Any sample SQL is framed as illustrative or placeholder content, not as an executed answer.
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
- Demo-only data shown in UI: the page must keep sample-only labeling visible.
- Timed mode selected before timed behavior exists: the page must label timed behavior as unavailable or future work.

## Out of scope for Phase 1

- Real SQL query execution.
- Exact-result grading and expected result comparison.
- AI grading or explanations.
- Durable progress tracking.
- Authentication or user-specific catalog state.
- Production Times refresh process or scheduled ingestion.
- Broad responsive design polish beyond clear catalog usability.
- Non-developer exercise authoring workflows.

## Success signals

Phase 1 is successful when a reviewer can:

- See a catalog-backed dataset and exercise list in the app.
- Identify which catalog entries are demo-only or placeholder-backed.
- Select or navigate to an exercise without SQL execution or grading being implied.
- Add or review a catalog entry through structured data and focused tests.
- Run the documented validation commands successfully.

## Open questions

- How many initial Times Archive exercises should Phase 1 include before implementation is considered complete?
- Should Phase 1 expose a dedicated catalog route, integrate catalog browsing into `/practice`, or both?
- Should exercise entries include concept tags, estimated time, or learning objectives in Phase 1?
- Should sample SQL remain visible for every exercise, or should it be moved behind a hint/placeholder pattern?
- Should exercise details reserve fields for future expected results while keeping exact grading out of scope?
- What is the exact not-found behavior for unknown dataset or exercise routes?
- Which production Times source/schema decision must be resolved before moving from demo catalog to production catalog?
