# Phase 0 implementation plan

## Status

Implemented. This plan was approved and completed through the tracked Phase 0 Linear issues.

## Source

- PRD: `prd/phase-0-product-scaffolding.md`
- Linear epic: `TIM-17`
- Child issues: `TIM-18`, `TIM-19`, `TIM-20`, `TIM-21`, `TIM-22`, `TIM-23`

## Planning decisions

- **Web stack:** Use Python 3.12 with FastAPI, server-rendered templates, and minimal JavaScript. This keeps the scaffold close to the existing `times-api` Python ecosystem while still providing routes, production serving, lint/static checks, tests, and a path to richer browser interactions later.
- **Progress model:** Use static/local placeholder data only. Do not add accounts, durable storage, or a persistence abstraction in Phase 0.
- **Times dataset:** Use sample data and schema references from `https://github.com/mikael-lh/times-api` as the initial Times dataset source. Commit only a tiny demo fixture set in SQL Gym and document provenance clearly.
- **SQL dialect:** Use PostgreSQL-compatible SQL as the first teaching dialect. Phase 0 should not execute SQL, but copy and domain metadata should describe future exercises as PostgreSQL-targeted unless a later PRD changes dialect support.
- **Domain models:** Use Pydantic models for placeholder dataset, exercise, attempt, grading, and progress data. The fixture-backed data is JSON-like, so runtime validation is useful without adding custom abstraction.
- **Production build:** Use `uv build` as the Phase 0 production build command. The scaffold should build a Python package even before deployment packaging is finalized.
- **Accessibility baseline:** Use semantic HTML, keyboard-reachable controls, visible focus states, sufficient contrast, and a basic responsive layout.

## Milestones

### 1. `TIM-19` - Choose stack and developer workflow

**Goal:** Establish the scaffold tooling before product UI work starts.

**Files to create or modify:**

- `pyproject.toml` - define Python 3.12 project metadata, dependencies, package build metadata, and scripts/tool configuration.
- `uv.lock` - lock Python dependencies.
- `app/` - add the minimum FastAPI package structure.
- `templates/` and `static/` - reserve server-rendered UI and stylesheet locations.
- `tests/` - add the initial test package.
- `README.md` - document selected stack and commands.

**Implementation notes:**

- Prefer FastAPI, Jinja2 templates, `uv`, pytest, ruff, and mypy.
- Keep JavaScript minimal in Phase 0; add HTMX or a richer editor package only when an approved feature needs it.
- Configure the app so `uv run fastapi dev app.main:app` or an equivalent documented command starts local development.
- Configure `uv build` as the production build command and document what artifact it creates.
- Add a test runner because the PRD requires a test command, but keep initial coverage small.

**Acceptance criteria covered:** R1, R7.

**Checks:** `uv sync`, `uv build`, `uv run ruff check .`, `uv run mypy .`, `uv run pytest`, `./scripts/validate-env.sh`.

**Risks:** Dependency setup may need a Cursor Cloud environment update if installs are slow or missing system tooling.

### 2. `TIM-20` - Create web app scaffold and app shell

**Goal:** Make the product direction visible without implying finished SQL functionality.

**Files to create or modify:**

- `app/main.py` - FastAPI app, routes, and static/template mounting.
- `templates/base.html` and `templates/index.html` - page shell and landing surface with SQL Gym name, positioning, and core loop.
- `static/styles.css` - baseline layout, placeholder states, and focus styles.
- Optional Python view/model helpers if route data needs structure.
- Tests for rendered shell content.

**Implementation notes:**

- Present the flow: pick dataset, pick difficulty, choose timed or untimed, complete exercise, get graded, move next.
- Mark unimplemented behavior with labels such as "Coming soon", disabled controls, or placeholder copy.
- Avoid fake working interactions for SQL execution or grading.

**Acceptance criteria covered:** R1, R2, R3.

**Checks:** `uv run ruff check .`, `uv run mypy .`, `uv run pytest`, manual browser check with screenshot/video once UI exists.

**Risks:** UI can overpromise functionality; keep placeholder language explicit.

### 3. `TIM-18` - Define domain model boundaries

**Goal:** Name the future product concepts without binding Phase 0 to storage, SQL execution, or AI services.

**Files to create or modify:**

- `app/domain/datasets.py` - dataset type and Times sample dataset metadata.
- `app/domain/exercises.py` - exercise type and placeholder exercise metadata.
- `app/domain/attempts.py` - attempt type without execution behavior.
- `app/domain/grading.py` - grading result type with placeholder statuses.
- `app/domain/progress.py` - progress summary type using static/demo-only data.
- `app/fixtures/times/` - tiny Times sample fixture files derived from `times-api`.
- Focused tests for exported placeholder data and model assumptions.

**Implementation notes:**

- Keep domain modules framework-agnostic and typed with Pydantic models.
- Use immutable placeholder data that the UI can consume.
- Capture sample provenance from `times-api` schema/data sources in fixture metadata or docs.
- Do not add database clients, AI clients, SQL parsers, or execution engines.

**Acceptance criteria covered:** R4, R5, R6.

**Checks:** `uv run ruff check .`, `uv run mypy .`, `uv run pytest`.

**Risks:** Types may become too detailed; keep them lightweight and replaceable.

### 4. `TIM-22` - Add practice flow placeholders

**Goal:** Show where dataset selection, difficulty, mode, editor, grading, and progress will live.

**Files to create or modify:**

- Practice route, such as `GET /practice` in `app/main.py`.
- Templates or template partials for dataset selection, difficulty, mode, SQL editor, grading feedback, and progress.
- Static data imports from the domain modules.
- Tests for placeholder labels and disabled or future-work states.

**Implementation notes:**

- Reference the Times dataset as the first dataset using committed demo samples derived from `times-api`.
- Label SQL exercise metadata as PostgreSQL-targeted, while keeping SQL execution out of Phase 0.
- Use static progress data and label it demo-only.
- Provide non-functional editor and grading placeholders unless a later approved PRD expands scope.

**Acceptance criteria covered:** R2, R3, R5, R6.

**Checks:** `uv run ruff check .`, `uv run mypy .`, `uv run pytest`, manual browser check with screenshot/video.

**Risks:** Placeholder controls must not submit or grade anything.

### 5. `TIM-21` - Add baseline lint, test, and build checks

**Goal:** Make future PRs easy to validate.

**Files to create or modify:**

- Python package build configuration if the scaffold needs extra metadata beyond `pyproject.toml`.
- Test configuration files for pytest if needed.
- Initial tests for the app shell, practice placeholders, and domain data.
- `scripts/validate-env.sh` - include app command checks once the stack exists.
- Optional CI workflow only if repo convention or user direction calls for it.

**Implementation notes:**

- Keep tests small and behavior-focused.
- Ensure commands documented in `README.md` match `uv` commands exactly.
- Include `uv build` in docs and validation so the PRD production build acceptance criterion is covered.
- Avoid broad test infrastructure beyond Phase 0 needs.

**Acceptance criteria covered:** R1.

**Checks:** `uv build`, `uv run ruff check .`, `uv run mypy .`, `uv run pytest`, `./scripts/validate-env.sh`.

**Risks:** Tests can become brittle if they assert layout details instead of user-visible content and placeholder states.

### 6. `TIM-23` - Update developer documentation

**Goal:** Make the scaffold easy to run and review.

**Files to create or modify:**

- `README.md` - setup, dev, build, lint, test, and workflow notes.
- Optional linked developer doc if the README becomes too long.
- `prd/README.md` only if implementation changes require status updates.

**Implementation notes:**

- State clearly what works in Phase 0 and what is a placeholder.
- Preserve the workflow gates: future product work still needs a PRD, plan, implementation PR, and pre-review.
- Document remaining follow-up decisions: production Times refresh process, grading model, persistence, auth, and AI provider.

**Acceptance criteria covered:** R7.

**Checks:** `./scripts/validate-env.sh`, `git diff --check`, and app checks listed in the README.

**Risks:** Documentation can drift from scripts; validate commands before handoff.

## Requirement coverage

| PRD item | Covered by |
|----------|------------|
| R1. Web app scaffold | `TIM-19`, `TIM-20`, `TIM-21`, `TIM-23` |
| R2. Product shell | `TIM-20`, `TIM-22` |
| R3. Initial navigation and layout boundaries | `TIM-20`, `TIM-22` |
| R4. Domain model boundaries | `TIM-18` |
| R5. Initial Times dataset placeholder | `TIM-18`, `TIM-22`, `TIM-23` |
| R6. Progress tracking placeholder | `TIM-18`, `TIM-22`, `TIM-23` |
| R7. Documentation | `TIM-19`, `TIM-23` |

## Out of scope

- Real SQL query execution.
- Exact-result grading.
- AI grading or explanations.
- Full exercise catalog.
- Authentication or persistent user accounts.
- Durable progress storage.
- Exercise authoring tooling.
- Full visual polish beyond a clear initial shell.

## Approval request

Approve this plan before implementation starts. After approval, the first implementation branch should start with `TIM-19`.
