# Phase 0 implementation plan

## Status

Proposed for approval. Do not write application code from this plan until the user approves it.

## Source

- PRD: `prd/phase-0-product-scaffolding.md`
- Linear epic: `TIM-17`
- Child issues: `TIM-18`, `TIM-19`, `TIM-20`, `TIM-21`, `TIM-22`, `TIM-23`

## Planning decisions

- **Web stack:** Use Next.js with TypeScript and React. This gives SQL Gym a conventional web app scaffold, routing, production build support, lint/static checks, and a straightforward path for future server-side features without adding a separate backend in Phase 0.
- **Progress model:** Use static/local placeholder data only. Do not add accounts, durable storage, or a persistence abstraction in Phase 0.
- **Times dataset:** Reference the Times dataset as the first intended dataset, but keep source and schema selection as a documented follow-up decision.
- **SQL dialect:** Do not enforce a dialect in Phase 0. Use copy that says later exercises are expected to target a Postgres-style dialect unless a later PRD decides otherwise.
- **Accessibility baseline:** Use semantic HTML, keyboard-reachable controls, visible focus states, sufficient contrast, and a basic responsive layout.

## Milestones

### 1. `TIM-19` - Choose stack and developer workflow

**Goal:** Establish the scaffold tooling before product UI work starts.

**Files to create or modify:**

- `package.json` - add scripts for `dev`, `build`, `lint`, and `test`.
- `package-lock.json` - lock npm dependencies.
- `next.config.*`, `tsconfig.json`, `eslint.config.*` - configure Next.js, TypeScript, and lint/static checks.
- `src/` or `app/` scaffold files - add only the minimum files required by the chosen Next.js app structure.
- `README.md` - document selected stack and commands.

**Implementation notes:**

- Prefer the current stable Next.js app router with TypeScript.
- Keep configuration minimal and generated defaults intact unless the repo needs a specific change.
- Add a test runner only if it can be justified by the Phase 0 acceptance criteria; keep initial coverage small.

**Acceptance criteria covered:** R1, R7.

**Checks:** install, `npm run build`, `npm run lint`, `npm test`, `./scripts/validate-env.sh`.

**Risks:** Dependency setup may need a Cursor Cloud environment update if installs are slow or missing system tooling.

### 2. `TIM-20` - Create web app scaffold and app shell

**Goal:** Make the product direction visible without implying finished SQL functionality.

**Files to create or modify:**

- `app/page.tsx` or equivalent home route - landing surface with SQL Gym name, positioning, and core loop.
- `app/layout.tsx` and global styles - page shell, metadata, and baseline layout.
- Component files under `src/components/` or `app/_components/` - reusable sections for core loop, placeholder cards, and status badges.
- Tests for rendered shell content.

**Implementation notes:**

- Present the flow: pick dataset, pick difficulty, choose timed or untimed, complete exercise, get graded, move next.
- Mark unimplemented behavior with labels such as "Coming soon", disabled controls, or placeholder copy.
- Avoid fake working interactions for SQL execution or grading.

**Acceptance criteria covered:** R1, R2, R3.

**Checks:** `npm run build`, `npm run lint`, `npm test`, manual browser check with screenshot/video once UI exists.

**Risks:** UI can overpromise functionality; keep placeholder language explicit.

### 3. `TIM-18` - Define domain model boundaries

**Goal:** Name the future product concepts without binding Phase 0 to storage, SQL execution, or AI services.

**Files to create or modify:**

- `src/domain/datasets.ts` - dataset type and Times placeholder record.
- `src/domain/exercises.ts` - exercise type and placeholder exercise metadata.
- `src/domain/attempts.ts` - attempt type without execution behavior.
- `src/domain/grading.ts` - grading result type with placeholder statuses.
- `src/domain/progress.ts` - progress summary type using static/demo-only data.
- Focused tests for exported placeholder data and type-level assumptions where practical.

**Implementation notes:**

- Keep domain modules framework-agnostic.
- Use immutable placeholder data that the UI can consume.
- Do not add database clients, AI clients, SQL parsers, or execution engines.

**Acceptance criteria covered:** R4, R5, R6.

**Checks:** `npm run lint`, `npm test`, `npm run build`.

**Risks:** Types may become too detailed; keep them lightweight and replaceable.

### 4. `TIM-22` - Add practice flow placeholders

**Goal:** Show where dataset selection, difficulty, mode, editor, grading, and progress will live.

**Files to create or modify:**

- Practice route, such as `app/practice/page.tsx`.
- Placeholder components for dataset selection, difficulty, mode, SQL editor, grading feedback, and progress.
- Static data imports from the domain modules.
- Tests for placeholder labels and disabled or future-work states.

**Implementation notes:**

- Reference the Times dataset as intended first dataset.
- Use static progress data and label it demo-only.
- Provide non-functional editor and grading placeholders unless a later approved PRD expands scope.

**Acceptance criteria covered:** R2, R3, R5, R6.

**Checks:** `npm run build`, `npm run lint`, `npm test`, manual browser check with screenshot/video.

**Risks:** Placeholder controls must not submit or grade anything.

### 5. `TIM-21` - Add baseline lint, test, and build checks

**Goal:** Make future PRs easy to validate.

**Files to create or modify:**

- Test configuration files for the selected runner.
- Initial tests for the app shell, practice placeholders, and domain data.
- `scripts/validate-env.sh` - include app command checks once the stack exists.
- Optional CI workflow only if repo convention or user direction calls for it.

**Implementation notes:**

- Keep tests small and behavior-focused.
- Ensure commands documented in `README.md` match scripts exactly.
- Avoid broad test infrastructure beyond Phase 0 needs.

**Acceptance criteria covered:** R1.

**Checks:** `npm run build`, `npm run lint`, `npm test`, `./scripts/validate-env.sh`.

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
- Document remaining follow-up decisions: Times source/schema, SQL dialect, grading model, persistence, auth, and AI provider.

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
