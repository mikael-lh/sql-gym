# Phase 5 manual test plan

Console workspace: single-page practice with JSON APIs, drawer navigation, and dismissible grading modal. Run with Postgres + imported Times data ([times-data-setup.md](times-data-setup.md)).

## 1. Entry and redirects

1. Open `/` → redirects to `/practice/...` workspace (no catalog card grid).
2. Bookmark `/practice/times-archive/times-archive-014` → workspace loads on that exercise.
3. Open `/practice/interview/start` → redirects to `/practice`.

## 2. Run SQL without reload

1. Enter `SELECT section_name FROM times_archive LIMIT 5;` → **Run SQL**.
2. Confirm the output console updates and the page does not reload.
3. Refresh the page → last run output restores in the console.

## 3. Submit and grading modal

1. Submit correct SQL for the exercise → modal shows **Passed** and summary → **OK** dismisses.
2. Submit incorrect SQL → modal shows **Not yet correct** → **OK** dismisses.
3. Press **Escape** while the modal is open → modal closes.

## 4. Timed exercise

1. Open a `Timed` exercise (e.g. `times-archive-005`).
2. **Start timed exercise** → countdown runs.
3. Let timer expire or submit manually → grading modal appears; progress cookie updates.

## 5. Drawer and in-place navigation

1. **Exercise list** → drawer shows badges (Not started / Attempted / Passed).
2. Select another exercise → URL updates via client navigation; left panel and editor update without full reload.
3. **Previous** / **Next** move within the filtered set.

## 6. Filters

1. Set difficulty **Beginner** → full navigation to first eligible exercise URL with query params.
2. If the current exercise is outside the filter, server redirects to the first eligible exercise.

## 7. Progress

1. Pass an exercise → passed count increments in the workspace header.
2. **Clear progress** → passed count resets; drawer badges refresh on reopen.
