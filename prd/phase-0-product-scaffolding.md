# Phase 0 product scaffolding PRD

## Status

Approved for planning. This phase should not be implemented until an implementation plan is created from it and approved.

## Source vision

This phase supports the SQL Gym product vision in `prd/00-product-vision.md`.

Phase 0 is the foundation for a web app where users can pick a dataset, choose difficulty and timed or untimed format, complete SQL exercises, receive grading, and track progress.

## Problem

SQL Gym needs a stable product and engineering foundation before building the exercise loop. Without a clear scaffold, early feature work could couple UI, datasets, grading, and progress tracking too tightly or make later testing and review difficult.

## Goals

- Establish a runnable web app foundation.
- Define the local development workflow for future contributors and agents.
- Create the initial product shell for the SQL practice experience.
- Define boundaries for datasets, exercises, grading, attempts, and progress tracking.
- Add baseline lint, test, and build commands for future implementation PRs.
- Leave product feature implementation small enough for focused follow-up PRs.

## Non-goals

- Executing user SQL against real datasets.
- Implementing exact-result grading.
- Implementing AI grading or explanations.
- Building the full exercise catalog.
- Implementing authentication or persistent user accounts.
- Shipping timed mode behavior beyond scaffolded routes or placeholders.

## Users and use cases

### Learner

As a SQL learner, I want the app to open cleanly and show the intended practice flow so I understand what SQL Gym will let me do.

### Future implementer

As a future implementer, I want clear module boundaries and dev commands so I can add datasets, exercises, grading, and progress without reworking the app foundation.

### Reviewer

As a reviewer, I want the scaffold to be easy to run, test, and inspect so each future feature PR can be evaluated against the PRD.

## Requirements

### R1. Web app scaffold

The project must include a runnable web app scaffold with documented commands for development, build, lint, and tests.

Acceptance criteria:

- A contributor can install dependencies and run the app locally using commands documented in the repo.
- A production build command exists.
- A lint or static check command exists.
- A test command exists, even if the initial test coverage is intentionally small.

### R2. Product shell

The app must include an initial shell that communicates the SQL Gym direction without pretending completed features exist.

Acceptance criteria:

- The shell includes the SQL Gym name and short positioning.
- The shell presents the intended core loop: pick dataset, pick difficulty, choose timed or untimed, complete exercise, get graded, move next.
- Unimplemented capabilities are clearly marked as placeholders, disabled controls, or future work.

### R3. Initial navigation and layout boundaries

The scaffold must make room for the main MVP surfaces.

Acceptance criteria:

- There is a home or landing surface.
- There is a practice surface or placeholder for selecting dataset, difficulty, and mode.
- There is a clear place for the future SQL editor.
- There is a clear place for future grading feedback.
- There is a clear place for future progress tracking.

### R4. Domain model boundaries

The scaffold must define lightweight domain types or interfaces for future features.

Acceptance criteria:

- Dataset, exercise, attempt, grading result, and progress concepts are named and documented in code or module structure.
- The boundaries do not require a database, AI provider, or SQL execution engine in Phase 0.
- Future phases can replace placeholder data without rewriting the product shell.

### R5. Initial Times dataset placeholder

The scaffold must reserve a clear place for the initial Times dataset.

Acceptance criteria:

- The UI or placeholder data references the Times dataset as the first intended dataset.
- The PR or docs identify that canonical source/schema selection remains a follow-up decision.
- No fake production dataset is presented as final.

### R6. Progress tracking placeholder

The scaffold must make progress tracking visible as an MVP requirement while avoiding premature persistence decisions.

Acceptance criteria:

- The shell includes a progress tracking area or placeholder.
- The implementation does not require user accounts unless a later PRD approves that scope.
- Any sample progress data is clearly static or demo-only.

### R7. Documentation

The repo must explain how to work with the scaffold.

Acceptance criteria:

- The root README or a linked developer doc includes setup, run, build, lint, and test commands.
- The docs state which Phase 0 items are placeholders versus working behavior.
- The docs preserve the PRD workflow gates for future product work.

## Out of scope for Phase 0

- Real SQL query execution.
- Real grading.
- AI provider integration.
- User authentication.
- Durable progress storage.
- Exercise authoring tooling.
- Full responsive or visual design polish beyond a clear initial shell.

## Suggested Linear breakdown

- Phase 0 | Choose stack and developer workflow.
- Phase 0 | Create web app scaffold and app shell.
- Phase 0 | Add practice flow placeholders.
- Phase 0 | Define domain model boundaries.
- Phase 0 | Add baseline lint, test, and build checks.
- Phase 0 | Update developer documentation.

## Success signals

Phase 0 is successful when a reviewer can:

- Run the app locally.
- See the intended SQL Gym practice flow.
- Identify placeholders versus working behavior.
- Run build, lint, and test commands.
- Understand where future dataset, exercise, grading, and progress work should go.

## Open questions

- Which web stack should the implementation plan choose?
- Should Phase 0 use local-only progress placeholders or introduce a persistence abstraction?
- What is the canonical source and schema for the initial Times dataset?
- Which SQL dialect should later phases target first?
- What accessibility and responsive layout baseline should Phase 0 enforce?
