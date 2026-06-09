# Phase 4 manual test plan

Interview sessions, session payload slimming, and catalog copy fixes. Run with Postgres + imported Times data ([times-data-setup.md](times-data-setup.md)).

## 1. Start interview session

1. Open `/practice` → **Start interview session**.
2. Confirm length options 3, 5, 8, Unlimited and optional difficulty filter.
3. Start a **3-question** session → lands on first catalog exercise with **Question 1 of 3** chrome.

## 2. Mixed timed + untimed queue

1. Note whether the current exercise is Timed or Untimed.
2. Timed: timer panel appears; Untimed: no timer panel.
3. Submit (pass or fail) → grading panel visible → **Next question**.

## 3. Progress cookie on interview submit

1. Submit an exercise in interview mode.
2. DevTools → `sql_gym_progress` cookie updates (pass/attempt).
3. Open the same exercise via casual `/practice/...` — badge reflects submit.

## 4. Advance and end early

1. After grading, **Next question** advances index and URL.
2. On any graded question, **End session early** → summary with outcomes so far.

## 5. Unlimited session (spot check)

1. Start **Unlimited** with no difficulty filter.
2. Confirm **Question N** label (no fixed “of Y” cap) and queue follows catalog order.

## 6. Resume and abandon

1. Mid-session, go to `/practice` or home → **Resume interview** banner.
2. Resume returns to current question.
3. **Abandon session** → banner gone; `/practice/interview/start` shows no active session.

## 7. Large-result grading (session slimming)

1. Open `times-archive-003` (wide grid) in casual or interview mode.
2. Submit a passing query → `#grading-title` and pass/fail copy render (session stores ≤25 preview rows).

## 8. Catalog copy spot-check

1. Open `times-archive-011` and `times-archive-014`.
2. Prompts and sample SQL reference **1920** dates matching gradable SQL.

## 9. Summary

1. Complete a short session or end early.
2. Summary lists exercises, pass/fail, elapsed, links to review.
3. Revisiting summary after view starts fresh (session cleared).
