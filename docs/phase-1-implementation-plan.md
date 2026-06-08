# Phase 1 implementation plan

## Status

Approved by the user. Do not write application code outside the scoped Linear issue being implemented.

## Source

- PRD: `prd/phase-1-dataset-exercise-catalog.md`
- Linear epic: `TIM-24`
- Child issues: `TIM-25`, `TIM-26`, `TIM-27`, `TIM-28`, `TIM-29`

## Planning decisions

- **Catalog exposure:** Integrate catalog browsing into the practice flow. Do not add a standalone catalog route in Phase 1.
- **Initial content:** Include 50 Times Archive exercises.
- **Times data status:** Treat the Times source/schema as production-ready for Phase 1 catalog use, while preserving provenance metadata.
- **Exercise metadata:** Include concept tags, estimated time, learning objectives, hint/sample SQL, placeholder/availability status, and reserved future expected-result fields.
- **Sample SQL:** Hide sample SQL behind a hint or placeholder pattern by default.
- **Future expected results:** Reserve structured expected-result fields without implementing exact grading.
- **Unknown routes:** Return a user-friendly 404 for unknown dataset or exercise detail routes; use inline empty states for empty filter results.
- **Non-goals:** Do not add SQL execution, exact-result grading, AI feedback, authentication, durable progress, scheduled Times refresh automation, or non-developer exercise authoring tooling.

## Milestones

### 1. `TIM-25` - Catalog domain model

**Goal:** Establish catalog types and validation boundaries before adding the 50-exercise dataset.

**Files to create or modify:**

- `src/app/domain/datasets.py` - production-ready Times dataset metadata and provenance fields.
- `src/app/domain/exercises.py` - richer exercise metadata fields.
- `src/app/domain/catalog.py` - catalog container and validation helpers.
- `tests/test_domain.py` - catalog metadata and validation tests.

**Implementation notes:**

- Keep models Pydantic-based, immutable, and framework-agnostic.
- Reject exercises that reference unknown datasets.
- Keep PostgreSQL as the only target dialect unless a later approved PRD changes that.
- Reserve expected-result fields as metadata only; do not compare or grade results.

**Acceptance criteria covered:** R1, R2, R4, R5.

**Checks:** `uv run pytest tests/test_domain.py`, `uv run ruff check .`, `uv run mypy .`.

**Risks:** Over-designing catalog abstractions; keep the API small and shaped by the 50 Times exercises.

### 2. `TIM-27` - Times exercise catalog data

**Goal:** Populate the Times catalog with the required initial 50 exercises.

**Files to create or modify:**

- `src/app/fixtures/times/` or a new catalog data location under `src/app/`.
- `tests/test_domain.py` - count, metadata, and consistency tests.

**Implementation notes:**

- Include stable ids, dataset id, title, prompt, difficulty, mode, target dialect, concept tags, estimated time, learning objectives, placeholder/availability status, hint/sample SQL, and reserved future expected-result fields for every exercise.
- Keep exercise data reviewable; split into structured data rather than hard-coding 50 entries in templates.
- Keep sample SQL hidden-by-default in UI-facing fields.

**Acceptance criteria covered:** R2, R4, R5.

**Checks:** `uv run pytest tests/test_domain.py`, `uv run ruff check .`, `uv run mypy .`.

**Risks:** Content quality and consistency across 50 exercises; tests should catch missing metadata, not judge exercise pedagogy.

### 3. `TIM-29` - Practice-flow catalog browsing

**Goal:** Replace the single locked placeholder assumptions with catalog browsing inside the practice flow.

**Files to create or modify:**

- `src/app/practice.py` - catalog-backed context and filtering/grouping.
- `templates/practice.html` - catalog-backed dataset and exercise browsing.
- `static/styles.css` - minimal layout additions for cards/filters/empty states.
- `tests/test_app.py` - page rendering and placeholder-honesty tests.

**Implementation notes:**

- Do not add a standalone `/catalog` route.
- Show datasets and exercises only when users choose the practice flow.
- Preserve visible no-SQL-execution, no-grading, and no-durable-progress copy.

**Acceptance criteria covered:** R3, R4, R5.

**Checks:** `uv run pytest tests/test_app.py`, `uv run ruff check .`, `uv run mypy .`, manual browser check/video.

**Risks:** UI can imply features work; keep disabled/placeholder language explicit.

### 4. `TIM-28` - Exercise preview and route states

**Goal:** Let a learner open a catalog-backed exercise preview from the practice flow.

**Files to create or modify:**

- `src/app/main.py` - practice-specific exercise detail route and 404 handling.
- `src/app/practice.py` - lookup helpers and preview context.
- `templates/practice_exercise.html` - exercise preview page.
- `templates/404.html` or equivalent user-friendly not-found response.
- `tests/test_app.py` - detail, hint, 404, and empty-state tests.

**Implementation notes:**

- Route should be practice-specific, such as `/practice/<dataset_id>/<exercise_id>`, not a standalone catalog route.
- Show metadata, learning objectives, tags, estimated time, and placeholder-safe prompt content.
- Hide sample SQL behind a hint or placeholder pattern by default.
- Return a user-friendly 404 for unknown dataset or exercise ids.

**Acceptance criteria covered:** R3, R4, edge cases.

**Checks:** `uv run pytest tests/test_app.py`, `uv run ruff check .`, `uv run mypy .`, manual browser check/video.

**Risks:** Route shape may need refinement during implementation; keep it small and linked from `/practice`.

### 5. `TIM-26` - Catalog docs and validation

**Goal:** Keep docs and validation aligned after Phase 1 behavior changes.

**Files to create or modify:**

- `README.md` - Phase 1 working behavior and placeholder boundaries if they change.
- `tests/test_developer_workflow.py` - docs guard updates if README wording changes.

**Implementation notes:**

- Keep `./scripts/validate-env.sh` as the full validation command.
- Document that catalog browsing works in the practice flow, while SQL execution, grading, AI, auth, and durable progress remain out of scope.

**Acceptance criteria covered:** R5.

**Checks:** `uv run pytest tests/test_developer_workflow.py`, `uv run pytest`, `uv run ruff check .`, `uv run mypy .`, `./scripts/validate-env.sh`, `git diff --check`.

**Risks:** Docs can drift from UI copy; guard high-level claims with tests where practical.

## Requirement coverage

| PRD item | Covered by |
|----------|------------|
| R1. Dataset catalog foundation | `TIM-25`, `TIM-27` |
| R2. Exercise catalog foundation | `TIM-25`, `TIM-27` |
| R3. Catalog browse and selection surface | `TIM-29`, `TIM-28` |
| R4. Placeholder honesty and boundaries | `TIM-25`, `TIM-27`, `TIM-29`, `TIM-28` |
| R5. Developer and reviewer workflow | `TIM-25`, `TIM-27`, `TIM-29`, `TIM-28`, `TIM-26` |

## Out of scope

- Real SQL query execution.
- Exact-result grading or expected-result comparison.
- AI grading or explanations.
- Authentication, accounts, or personalization.
- Durable progress tracking or attempt history.
- Scheduled Times refresh automation.
- Non-developer exercise authoring tooling.
- Standalone catalog route.

## Approval

Approved by the user after local `implement-from-prd` planning. Implement only one Linear issue at a time using `sql-gym-implement-issue`, or use `sql-gym-run-phase` when the user has authorized sequential autonomous execution.
