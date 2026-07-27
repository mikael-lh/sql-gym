import {
  buildExercisesListUrl,
  buildRunUrl,
  buildSubmitUrl,
  getSqlInput,
  readWorkspaceConfig,
} from "./workspace/api-client.js";
import { formatCell, formatTime, parseElapsedDisplay } from "./workspace/format.js";
import { initWorkspaceNavigation } from "./workspace/navigation.js";
import {
  createGradingModal,
  renderExecutionError,
  renderQueryResult,
  renderConsoleAttempt,
  updateNavigationButtons,
  updateProgressUi,
} from "./workspace/render.js";
import { initWorkspaceStopwatch } from "./workspace/stopwatch.js";

export function initPracticeWorkspace() {
  const config = readWorkspaceConfig();
  const consoleEl = document.getElementById("workspace-console");
  const runButton = document.getElementById("workspace-run-sql");
  const submitButton = document.getElementById("workspace-submit-sql");
  const clearButton = document.getElementById("workspace-clear-progress");
  if (
    !config ||
    !(consoleEl instanceof HTMLElement) ||
    !(runButton instanceof HTMLButtonElement) ||
    !(submitButton instanceof HTMLButtonElement)
  ) {
    return;
  }

  const workspaceConfig = { ...config, filters: { ...config.filters } };
  renderConsoleAttempt(consoleEl, workspaceConfig.attempt);

  const modal = createGradingModal(
    submitButton,
    document.getElementById("workspace-next"),
    workspaceConfig,
  );
  let runInFlight = false;
  let submitInFlight = false;
  const initialProgress = workspaceConfig.progress ?? {};
  const alreadyPassed = initialProgress.status === "passed";
  const initialElapsedSeconds = parseElapsedDisplay(initialProgress.first_pass_elapsed);
  const stopwatch = initWorkspaceStopwatch({
    initialElapsedSeconds,
    stopped: alreadyPassed,
  });

  const submitForGrading = async () => {
    if (submitInFlight) {
      return;
    }
    const sqlInput = getSqlInput();
    if (!sqlInput) {
      return;
    }
    const sql = sqlInput.value.trim();
    if (!sql) {
      modal.show({
        passed: false,
        summary: "Enter SQL before submitting for grading.",
      });
      return;
    }

    submitInFlight = true;
    submitButton.disabled = true;
    submitButton.setAttribute("aria-busy", "true");

    const body = { sql };
    const elapsedSeconds = stopwatch.getElapsedSeconds();
    if (elapsedSeconds !== null) {
      body.elapsed_seconds = elapsedSeconds;
    }

    try {
      const response = await fetch(buildSubmitUrl(workspaceConfig), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const payload = await response.json();
      if (!response.ok) {
        const message = payload.error?.message ?? "Could not submit SQL for grading.";
        modal.show({ passed: false, summary: message });
        return;
      }
      if (payload.grading?.passed === true) {
        stopwatch.stop();
      }
      if (payload.grading) {
        modal.show(payload.grading);
      }
      if (payload.progress) {
        updateProgressUi(payload.progress);
      }
      if (payload.grading?.passed === true && elapsedSeconds !== null) {
        const firstPassElapsed = document.getElementById("workspace-first-pass-elapsed");
        if (firstPassElapsed instanceof HTMLElement) {
          firstPassElapsed.textContent = ` — solved in ${formatTime(elapsedSeconds)}`;
          firstPassElapsed.hidden = false;
        }
      }
    } catch {
      modal.show({
        passed: false,
        summary: "Network error while submitting SQL. Try again.",
      });
    } finally {
      submitInFlight = false;
      submitButton.disabled = false;
      submitButton.removeAttribute("aria-busy");
    }
  };

  runButton.addEventListener("click", async () => {
    if (runInFlight) {
      return;
    }
    const sqlInput = getSqlInput();
    if (!sqlInput) {
      return;
    }
    const sql = sqlInput.value.trim();
    if (!sql) {
      renderExecutionError(consoleEl, {
        message: "Enter SQL before running your query.",
        code: "empty_sql",
      });
      return;
    }

    runInFlight = true;
    runButton.disabled = true;
    runButton.setAttribute("aria-busy", "true");

    try {
      const response = await fetch(buildRunUrl(workspaceConfig), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sql }),
      });
      const payload = await response.json();
      if (!response.ok) {
        const error = payload.error ?? {
          message: "Could not run query.",
          code: "run_failed",
        };
        renderExecutionError(consoleEl, error);
        return;
      }
      renderQueryResult(consoleEl, payload);
    } catch {
      renderExecutionError(consoleEl, {
        message: "Network error while running SQL. Try again.",
        code: "network_error",
      });
    } finally {
      runInFlight = false;
      runButton.disabled = false;
      runButton.removeAttribute("aria-busy");
    }
  });

  submitButton.addEventListener("click", () => {
    void submitForGrading();
  });

  const renderDrawerLoading = () => {
    const drawerList = document.getElementById("workspace-drawer-list");
    if (!(drawerList instanceof HTMLElement)) {
      return;
    }
    drawerList.innerHTML =
      '<li class="workspace-drawer-loading"><p class="placeholder-note">Loading exercises…</p></li>';
  };

  const loadDrawerExercises = async () => {
    const drawerList = document.getElementById("workspace-drawer-list");
    const drawerCount = document.getElementById("workspace-drawer-count");
    if (!(drawerList instanceof HTMLElement)) {
      return;
    }
    renderDrawerLoading();
    const response = await fetch(buildExercisesListUrl(workspaceConfig.filters));
    if (!response.ok) {
      return;
    }
    const payload = await response.json();
    if (drawerCount instanceof HTMLElement) {
      drawerCount.textContent = `Showing ${payload.total} exercises`;
    }
    drawerList.innerHTML = payload.exercises
      .map((exercise) => {
        const active =
          exercise.id === workspaceConfig.exercise_id &&
          exercise.dataset_id === workspaceConfig.dataset_id
            ? ' aria-current="true"'
            : "";
        return `
          <li>
            <button type="button" class="workspace-drawer-item" data-dataset-id="${formatCell(exercise.dataset_id)}" data-exercise-id="${formatCell(exercise.id)}"${active}>
              <span>${formatCell(exercise.title)}</span>
              <span class="progress-badge progress-badge-${exercise.progress_status}">${formatCell(exercise.progress_label)}</span>
            </button>
          </li>`;
      })
      .join("");
  };

  if (clearButton instanceof HTMLButtonElement) {
    clearButton.addEventListener("click", async () => {
      clearButton.disabled = true;
      try {
        const response = await fetch("/api/practice/progress/clear", { method: "POST" });
        if (!response.ok) {
          return;
        }
        const clearPayload = await response.json();
        updateProgressUi(clearPayload.progress ?? {
          passed_count: 0,
          status: "not_started",
          label: "Not started",
        });
        await loadDrawerExercises();
      } finally {
        clearButton.disabled = false;
      }
    });
  }

  initWorkspaceNavigation({
    workspaceConfig,
    consoleEl,
    modal,
    stopwatch,
    loadDrawerExercises,
  });

  updateNavigationButtons(workspaceConfig.navigation);

  return { hideGradingModal: modal.hide };
}
