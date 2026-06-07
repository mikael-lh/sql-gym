---
name: write-prd
description: Create or revise a local PRD from codebase context. Use when defining product vision, phase scope, or a feature spec without relying on ChatPRD cloud.
---

# Write a local PRD

## Trigger

The user wants to create or revise product requirements for this repo.

## Source of truth

Use local markdown files under `prd/` as the authoritative product spec. Do not call ChatPRD MCP tools or require a ChatPRD cloud document.

## Workflow

1. Clarify the product scope.
   - If the requested scope is ambiguous, ask what product, phase, or feature should be specified.
   - If the user asks to draft with unknowns, proceed and list unresolved decisions under **Open questions**.
2. Explore repo context before drafting.
   - Read `prd/README.md`.
   - Read relevant existing `prd/*.md` files.
   - Inspect existing application code, data models, routes, API endpoints, tests, and docs if they exist.
3. Pick or create the local PRD file.
   - Product vision: `prd/00-product-vision.md`.
   - Phase scope: `prd/phase-N-short-name.md`.
   - Feature scope: `prd/feature-short-name.md` or another clear kebab-case name.
4. Draft the PRD with sections appropriate to the scope:
   - Status
   - Source context
   - Problem
   - Goals
   - Non-goals
   - Users and use cases
   - Requirements
   - Acceptance criteria
   - Edge cases and error states
   - Out of scope
   - Success signals
   - Open questions
5. Ground the PRD in repo context.
   - Cite local docs and files in prose when useful.
   - Do not invent requirements from informal assumptions.
   - Keep unknown product decisions as open questions.
6. Update `prd/README.md`.
   - Add or update the index row.
   - Update status accurately.
   - Name an active phase only when the user explicitly approves that phase.
7. Commit the PRD changes and open or update a draft PR.

## Guardrails

- Requirements belong in `prd/`, not chat-only notes.
- Keep one PRD focused on one product vision, phase, or feature.
- Do not write application code as part of this skill.
- Do not mark a phase active unless the user explicitly approves it.
- Preserve workflow gates in `.cursor/rules/workflow.mdc`.

## Output

- Local PRD saved under `prd/`.
- `prd/README.md` updated when needed.
- Summary of what the PRD covers.
- Open questions and approval needed before implementation.
