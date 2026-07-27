# Phase 7 manual test plan

Local LLM explain-on-fail checks for [prd/phase-7-local-llm-explain-on-fail.md](../prd/phase-7-local-llm-explain-on-fail.md).

## Prerequisites

- `./scripts/dev.sh` or equivalent: Postgres up, Times data imported
- **Single-worker** uvicorn (default): `uv run uvicorn app.main:app --reload`
- Optional for happy-path AI: [Ollama](https://ollama.com) installed and running on `http://127.0.0.1:11434`
- Browser with JavaScript enabled

Automated regression (no live Ollama required): `./scripts/validate-env.sh` and `uv run pytest`.

## 1. Failed submit → Explain with AI (Ollama up)

1. Ensure Ollama is running; start (or restart) the app so launch can pull `OLLAMA_MODEL` (default `llama3.2:3b`). First launch may take a while while the model downloads.
2. Open a workspace exercise; enter SQL that fails grading (e.g. wrong column names).
3. Click **Submit for grading** → modal shows **Not yet correct** and **Explain with AI**.
4. Confirm a **passed** submit modal (use a correct query on another attempt or exercise) does **not** show Explain with AI.
5. On a failed modal, click **Explain with AI** → status shows loading, then explanation text.
6. Dismiss with **OK** / Escape; progress badge remains **Attempted** (not rewritten by explain).

## 2. AI unavailable (Ollama down)

1. Stop Ollama (or set `OLLAMA_BASE_URL` to a closed port) and restart the app (should still start).
2. Submit a failing answer → **Explain with AI** still appears.
3. Click it → modal shows a clear server message such as “AI unavailable: …” (not a blank success).
4. Confirm run/submit grading still works without AI.

## 3. Session / attempt gating

1. Fail a submit, then click **Run SQL** (any valid SELECT) without submitting again.
2. Open explain (if still on an old modal, re-submit fail first): after a run-only attempt, explain should report no failed submit until another failing submit stores grading again.
3. Pass an exercise → explain is not offered on the passed modal.

## 4. Model cleanup on app stop

1. With Ollama up and `OLLAMA_KEEP_MODEL` unset/`0`, start the app so it pulls the model (or confirm the model is listed: `ollama list`).
2. Stop the app process (Ctrl-C / stop `dev.sh`).
3. Run `ollama list` — the configured model should be gone **if this app process had pulled it**. If the model was already installed before launch, the app does not delete it.
4. Optional: set `OLLAMA_KEEP_MODEL=1`, restart, stop again — model should remain installed.

## 5. Env defaults smoke

Confirm `.env.example` documents `OLLAMA_BASE_URL`, `OLLAMA_MODEL`, `OLLAMA_KEEP_MODEL`, and timeouts. Overrides in `.env` change pull/chat targets without code changes.

## Automated coverage

| Area | Tests |
|------|--------|
| Ollama client / lifespan | `tests/test_ollama_client.py` |
| Explain API + safe context | `tests/test_explain_api.py` |
| Explain modal UI | `tests/test_explain_modal.py` |
| Grading modal dismiss | `tests/test_grading_modal.py` |
