import {
  buildExerciseApiUrl,
  buildExercisePath,
  parseExerciseLocation,
} from "./api-client.js";
import { parseElapsedDisplay } from "./format.js";
import { applyExercisePayload, renderConsoleAttempt } from "./render.js";

export function initWorkspaceNavigation({
  workspaceConfig,
  consoleEl,
  modal,
  stopwatch,
  loadDrawerExercises,
}) {
  const drawer = document.getElementById("workspace-drawer");
  const drawerToggle = document.getElementById("workspace-drawer-toggle");
  const drawerClose = document.getElementById("workspace-drawer-close");
  const drawerList = document.getElementById("workspace-drawer-list");
  const prevButton = document.getElementById("workspace-prev");
  const nextButton = document.getElementById("workspace-next");

  const setDrawerOpen = (open) => {
    if (!(drawer instanceof HTMLElement) || !(drawerToggle instanceof HTMLButtonElement)) {
      return;
    }
    drawer.hidden = !open;
    drawerToggle.setAttribute("aria-expanded", open ? "true" : "false");
  };

  const loadExercise = async (datasetId, exerciseId, filters, { push = true } = {}) => {
    modal.hide();
    const response = await fetch(buildExerciseApiUrl(datasetId, exerciseId, filters));
    if (!response.ok) {
      window.location.assign(buildExercisePath(datasetId, exerciseId, filters));
      return;
    }
    const payload = await response.json();
    workspaceConfig.dataset_id = datasetId;
    workspaceConfig.exercise_id = exerciseId;
    workspaceConfig.filters = filters;
    workspaceConfig.navigation = payload.navigation;
    workspaceConfig.attempt = {
      query_result: payload.attempt?.query_result ?? null,
      execution_error: payload.attempt?.execution_error ?? null,
    };
    applyExercisePayload(payload);
    renderConsoleAttempt(consoleEl, workspaceConfig.attempt);
    const passed = payload.progress?.status === "passed";
    const elapsedSeconds = parseElapsedDisplay(payload.progress?.first_pass_elapsed);
    stopwatch.reset({ elapsedSeconds, keepStopped: passed });
    if (push) {
      window.history.pushState(
        { workspace: true },
        "",
        buildExercisePath(datasetId, exerciseId, filters),
      );
    }
    void loadDrawerExercises();
  };

  if (drawerToggle instanceof HTMLButtonElement) {
    drawerToggle.addEventListener("click", () => {
      const open = drawer instanceof HTMLElement && drawer.hidden;
      setDrawerOpen(Boolean(open));
      if (open) {
        void loadDrawerExercises();
      }
    });
  }
  if (drawerClose instanceof HTMLButtonElement) {
    drawerClose.addEventListener("click", () => setDrawerOpen(false));
  }

  if (drawerList instanceof HTMLElement) {
    drawerList.addEventListener("click", (event) => {
      const target = event.target;
      if (!(target instanceof HTMLElement)) {
        return;
      }
      const button = target.closest("[data-exercise-id]");
      if (!(button instanceof HTMLButtonElement)) {
        return;
      }
      const datasetId = button.dataset.datasetId;
      const exerciseId = button.dataset.exerciseId;
      if (!datasetId || !exerciseId) {
        return;
      }
      setDrawerOpen(false);
      void loadExercise(datasetId, exerciseId, workspaceConfig.filters);
    });
  }

  const wireNavButton = (button) => {
    if (!(button instanceof HTMLButtonElement)) {
      return;
    }
    button.addEventListener("click", () => {
      const targetUrl = button.dataset.targetUrl;
      if (!targetUrl) {
        return;
      }
      const url = new URL(targetUrl, window.location.origin);
      const parsed = parseExerciseLocation(url.pathname, url.search);
      if (!parsed) {
        return;
      }
      void loadExercise(parsed.dataset_id, parsed.exercise_id, parsed.filters, { push: true });
    });
  };
  wireNavButton(prevButton);
  wireNavButton(nextButton);

  const redirectForFilters = () => {
    const params = new URLSearchParams();
    const difficultyFilter = document.getElementById("workspace-filter-difficulty");
    if (difficultyFilter instanceof HTMLSelectElement && difficultyFilter.value) {
      params.set("difficulty", difficultyFilter.value);
    }
    const query = params.toString();
    window.location.assign(query ? `/practice?${query}` : "/practice");
  };
  const difficultyFilter = document.getElementById("workspace-filter-difficulty");
  if (difficultyFilter instanceof HTMLSelectElement) {
    difficultyFilter.addEventListener("change", redirectForFilters);
  }

  window.addEventListener("popstate", () => {
    const parsed = parseExerciseLocation(window.location.pathname, window.location.search);
    if (!parsed) {
      return;
    }
    void loadExercise(parsed.dataset_id, parsed.exercise_id, parsed.filters, { push: false });
  });

  return { loadExercise };
}
