# Phase 7 local LLM explain-on-fail PRD

## Status

**Approved and active** (2026-07-27). Implementation plan required via `implement-from-prd` before application code.

## Source context

Follows `prd/00-product-vision.md` and comes after `prd/phase-6-reliability-and-code-quality.md` (complete).

Phase 5–6 shipped a practice workspace with **strict grid-match grading**, a dismissible grading modal on submit, and progress cookies. Product vision still calls for AI explanations; earlier phases deferred AI. This phase adds the first AI learner feature using a **local LLM** (not a cloud provider).

Strict grading remains the source of truth for pass/fail. AI does not award credit or change grading outcomes.

## Problem

When a learner submits SQL that fails strict grading, they see a short pass/fail summary. They do not get an explanation of what went wrong or what to try next. Cloud AI would help but conflicts with a local-first preference: models and inference should run on the learner’s machine when available, with clear behavior when they are not.

Multi‑GB local model files should not linger indefinitely after the learner stops using the app for that session.

## Goals

- After a **failed** submit, offer an AI explanation of the failure grounded in the learner’s SQL and grading result.
- Use a **local LLM** via **native Ollama** (HTTP on localhost).
- When Ollama or the model is unavailable, show a clear **“AI unavailable”** message (do not silently hide the concept).
- When the **app session ends**, remove the pulled model weights so multi‑GB files do not hang around by default.
- Keep pass/fail and progress behavior unchanged except for the new explain-on-fail UX.

## Non-goals

- Cloud LLM providers (OpenAI, Anthropic, etc.).
- AI as the grading authority; partial credit; changing expected grids or `reference_sql`.
- On-demand “Ask AI” / hint buttons while writing SQL (before or without a failed submit).
- Explaining **passed** submits.
- Accounts, auth, or cross-device sync.
- New datasets, exercises, or a visual redesign of the workspace.
- Requiring Docker/Compose for Ollama (native install is the default path).
- Deleting the model on every explain request (only when the session ends).

## Users and use cases

Same learners as today, practicing in the workspace.

As a learner, after Submit fails, I want an explanation of why my result did not match so I can improve my next attempt.

As a learner on a machine without Ollama running, I want a clear “AI unavailable” message so I know how to enable explanations (or continue without them).

As a learner who cares about disk space, I want the large model cleaned up when I finish the app session so it does not stay installed forever by default.

## Resolved product decisions

| Topic | Decision |
|-------|----------|
| **Learner job** | Explain a **failed** submit (why it failed / what to try). |
| **When it appears** | **After failed submit only** (not a standing workspace button). |
| **Local runtime** | **Native Ollama** (HTTP to localhost). |
| **Unavailable** | Show clear **“AI unavailable”** (control/message visible; not silent hide-only). |
| **Grading truth** | Strict grid match unchanged; AI does not grant pass or partial credit. |
| **Model cleanup** | Remove the session’s pulled model when the **app session ends** — not per request. |

## Requirements

### A1. Explain failed submits with a local LLM

**Plain-language:** After grading fails, the learner can get a short explanation from a model running on their machine.

- On failed submit, the grading UX (modal or adjacent panel) offers an AI explanation action or auto-loads explanation once (exact chrome decided in the implementation plan; must remain “after failed submit only”).
- The explanation request includes enough context for a useful answer: exercise prompt (and related exercise fields as needed), learner SQL, and grading summary / mismatch signals already available to the server — **not** the full expected result grid if that would spoil the answer (implementation plan chooses a safe context pack).
- Responses are shown as learner-facing text; they must not change `grading.passed` or progress cookie updates.
- Passed submits do not trigger AI explanation.

Acceptance criteria:

- Failed submit → learner can see an AI explanation when Ollama + model are available.
- Passed submit → no AI explain flow.
- Pass/fail and progress badges behave as today aside from the new explain UI.

### A2. Native Ollama integration

**Plain-language:** The app talks to Ollama on the machine, not to a cloud API.

- Configurable base URL (default `http://127.0.0.1:11434`) and model name via env (documented in `.env.example`).
- Document how to install Ollama and pull/run the configured model for local/dev use.
- Cloud/agent environments without Ollama still run the rest of the app; AI paths degrade per A3.

Acceptance criteria:

- With Ollama running and the configured model available, explain-on-fail returns text.
- Integration does not require Docker for Ollama.

### A3. Clear “AI unavailable” when the model cannot be reached

**Plain-language:** If Ollama is down, the model is missing, or the request fails, the UI says so clearly.

- After a failed submit, if explanation cannot be produced, show an explicit **AI unavailable** (or equivalent) message with a short reason class: not running, model missing, timeout, etc. (exact copy in implementation).
- Do not pretend an explanation succeeded.
- Learner can still dismiss the grading modal and keep practicing.

Acceptance criteria:

- Stopping Ollama (or pointing at a bad URL) yields a visible unavailable state after a failed submit’s explain path — not a blank success.
- Happy-path grading without AI still works when AI is down.

### A4. Remove the model when the app session ends

**Plain-language:** Multi‑GB weights should not linger after the learner is done with this run of the app.

- On **app session end**, delete/remove the configured model from Ollama (e.g. `ollama rm` / equivalent API) so weights do not remain installed by default.
- Do **not** delete the model after every explain request.
- If cleanup fails (Ollama already stopped, permissions, etc.), log clearly and do not crash the process shutdown path.
- Document that the next session may need to re-pull the model (time/bandwidth tradeoff accepted).

**Session end (working definition for this PRD):** the **sql-gym application process** shutting down (e.g. uvicorn / `dev.sh` stop / lifespan shutdown). Browser tab close alone is **not** required to trigger cleanup in this phase (unreliable); see Open questions if a different meaning is preferred.

Acceptance criteria:

- After a session that pulled/used the model, stopping the app removes that model from Ollama when Ollama is still reachable at shutdown.
- Explain requests during the session do not remove the model between calls.
- Shutdown still completes if cleanup cannot run.

### A5. Docs and validation

- README / `.env.example` document Ollama URL, model name, and cleanup-on-shutdown behavior.
- Short Phase 7 manual test plan: failed submit + explain; unavailable; cleanup on stop.
- `./scripts/validate-env.sh` stays green; AI tests mock Ollama or skip when unreachable (same pattern as optional `DATABASE_URL`).

## Phase acceptance criteria

- [ ] After a failed submit, learners can get a local-LLM explanation when Ollama is available.
- [ ] AI never changes pass/fail or progress outcomes.
- [ ] Unavailable Ollama/model shows a clear AI unavailable message.
- [ ] Configured model is removed when the app process session ends (not per request).
- [ ] Docs and validation cover the new paths; app works without Ollama for non-AI flows.

## Edge cases and error states

| Case | Expected behavior |
|------|-------------------|
| Ollama not installed / not running | AI unavailable message; grading unchanged |
| Model not pulled yet | Pull on first explain in the session **or** unavailable with “model missing” (implementation plan picks one; if auto-pull, A4 still removes on session end) |
| Explain request timeout / Ollama error | AI unavailable (or retry-able error); no fake explanation |
| Learner passes on submit | No AI explain flow |
| Shutdown while Ollama already stopped | Cleanup skipped/logged; process exits cleanly |
| Multiple app workers | Implementation plan must avoid conflicting pull/rm races (prefer single-worker local dev assumption or document constraint) |

## Out of scope

- Partial-credit scoring or AI override of strict grids.
- Pre-submit / always-visible Ask AI.
- Cloud providers and API keys for hosted LLMs.
- Dockerized Ollama as a required setup (optional notes OK).
- Guaranteeing cleanup on browser close alone.

## Success signals

- Learners get useful post-fail explanations without leaving the workspace.
- Machines without Ollama still run sql-gym; AI failure mode is obvious.
- After stopping the app, the configured model is not left installed by default.

## Open questions

- **Exact UI chrome:** explain text inside the existing grading modal vs a follow-on panel — decide in `implement-from-prd`.
- **Context pack:** how much of expected columns/rows / reference SQL to send without spoiling answers.
- **Default model name / size:** pick a small default suitable for local CPU/GPU in the implementation plan.
- **Auto-pull on first explain?** vs require `ollama pull` beforehand.
- **“Session ends”:** confirm app-process shutdown is the intended trigger (vs browser session cookie end). **PRD assumes app-process shutdown** unless the user overrides.
- **Should cleanup be configurable** (env flag to keep the model installed for frequent local dev)?

## Approval

- [x] PRD scope approved by user (2026-07-27).
- [x] Phase 7 named active in `prd/README.md` (only after approval).
- [x] Implementation plan approved (via `implement-from-prd`) before any code changes.

## References

- `prd/00-product-vision.md` — AI explanations / mixed grading (this phase: explain only, not AI grading authority)
- `prd/phase-5-console-workspace.md` — workspace + grading modal
- `prd/phase-6-reliability-and-code-quality.md` — current complete phase
- `src/app/api/practice.py` — submit / grading JSON
- `static/js/workspace/render.js` — grading modal
- `.env.example`, `README.md`
