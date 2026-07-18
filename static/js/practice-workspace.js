function readWorkspaceConfig() {
  const configNode = document.getElementById("workspace-config");
  if (!(configNode instanceof HTMLScriptElement) || !configNode.textContent) {
    return null;
  }
  try {
    return JSON.parse(configNode.textContent);
  } catch {
    return null;
  }
}

function getSqlInput() {
  const input = document.getElementById("practice-sql-input");
  if (input instanceof HTMLTextAreaElement || input instanceof HTMLInputElement) {
    return input;
  }
  return null;
}

function formatCell(cell) {
  if (cell === null || cell === undefined) {
    return '<span class="null-cell">NULL</span>';
  }
  return String(cell)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function renderQueryResult(consoleEl, result) {
  const truncatedNote = result.truncated
    ? '<p class="placeholder-note">Showing the first 500 rows. Narrow your query to see a complete result.</p>'
    : "";
  const rowLabel = result.row_count === 1 ? "row" : "rows";
  const header = result.columns
    .map((column) => `<th scope="col">${formatCell(column)}</th>`)
    .join("");
  const body = result.rows
    .map(
      (row) =>
        `<tr>${row.map((cell) => `<td>${formatCell(cell)}</td>`).join("")}</tr>`,
    )
    .join("");

  consoleEl.innerHTML = `
    <div class="workspace-console-meta">
      <p class="eyebrow">Execution</p>
      <h3>Query result</h3>
      ${truncatedNote}
      <p class="catalog-count">${result.row_count} ${rowLabel} returned.</p>
    </div>
    <div class="workspace-console-results">
      <div class="result-table-wrap">
        <table class="result-table">
          <thead><tr>${header}</tr></thead>
          <tbody>${body}</tbody>
        </table>
      </div>
    </div>
  `;
}

function renderExecutionError(consoleEl, error) {
  consoleEl.innerHTML = `
    <div class="workspace-console-meta">
      <p class="eyebrow">Execution</p>
      <h3>Could not run query</h3>
      <p class="feedback feedback-error">${formatCell(error.message)}</p>
    </div>
  `;
}

function renderConsoleAttempt(consoleEl, attempt) {
  if (!attempt) {
    return;
  }
  if (attempt.execution_error) {
    renderExecutionError(consoleEl, attempt.execution_error);
    return;
  }
  if (attempt.query_result) {
    renderQueryResult(consoleEl, attempt.query_result);
  }
}

function buildRunUrl(config) {
  return `/api/practice/${config.dataset_id}/${config.exercise_id}/run`;
}

function buildSubmitUrl(config) {
  return `/api/practice/${config.dataset_id}/${config.exercise_id}/submit`;
}

function filtersToQuery(filters) {
  const params = new URLSearchParams();
  if (filters?.difficulty) {
    params.set("difficulty", filters.difficulty);
  }
  const query = params.toString();
  return query ? `?${query}` : "";
}

function buildExercisePath(datasetId, exerciseId, filters) {
  return `/practice/${datasetId}/${exerciseId}${filtersToQuery(filters)}`;
}

function buildExerciseApiUrl(datasetId, exerciseId, filters) {
  return `/api/practice/${datasetId}/${exerciseId}${filtersToQuery(filters)}`;
}

function buildExercisesListUrl(filters) {
  return `/api/practice/exercises${filtersToQuery(filters)}`;
}

function parseExerciseLocation(pathname, search) {
  const match = pathname.match(/^\/practice\/([^/]+)\/([^/]+)$/);
  if (!match) {
    return null;
  }
  const params = new URLSearchParams(search);
  return {
    dataset_id: match[1],
    exercise_id: match[2],
    filters: {
      difficulty: params.get("difficulty") ?? "",
    },
  };
}

function renderSchemaHtml(schema) {
  if (!schema?.tables?.length) {
    return "";
  }
  return schema.tables
    .map((table) => {
      const columns = table.columns
        .map((column) => {
          const description = column.description
            ? `<p class="workspace-schema-description">${formatCell(column.description)}</p>`
            : "";
          return `
            <div class="workspace-schema-column">
              <p class="workspace-schema-column-name"><code>${formatCell(column.name)}</code>
              <span class="workspace-schema-type">${formatCell(column.type)}</span></p>
              ${description}
            </div>`;
        })
        .join("");
      return `
        <div class="workspace-schema-table">
          <h3>${formatCell(table.name)}</h3>
          <div class="workspace-schema-columns">${columns}</div>
        </div>`;
    })
    .join("");
}

function setEditorSql(sql) {
  const config = document.getElementById("practice-editor-config");
  if (!(config instanceof HTMLElement) || typeof globalThis.resetPracticeEditor !== "function") {
    const input = getSqlInput();
    if (input) {
      input.value = sql;
    }
    return;
  }
  globalThis.resetPracticeEditor(config.dataset.hostId, config.dataset.inputId, sql);
}

function updateNavigationButtons(navigation) {
  const prevButton = document.getElementById("workspace-prev");
  const nextButton = document.getElementById("workspace-next");
  const footerPosition = document.getElementById("workspace-nav-position");
  const positionLabel = document.getElementById("workspace-position-label");
  if (prevButton instanceof HTMLButtonElement) {
    prevButton.disabled = !navigation?.prev_url;
    prevButton.dataset.targetUrl = navigation?.prev_url ?? "";
  }
  if (nextButton instanceof HTMLButtonElement) {
    nextButton.disabled = !navigation?.next_url;
    nextButton.dataset.targetUrl = navigation?.next_url ?? "";
  }
  if (footerPosition instanceof HTMLElement && navigation?.position_label) {
    footerPosition.textContent = navigation.position_label;
  }
  if (positionLabel instanceof HTMLElement && navigation?.position_label) {
    positionLabel.textContent = navigation.position_label;
  }
}

function collapseContextDisclosures() {
  for (const id of ["workspace-hint-details", "workspace-schema-details"]) {
    const details = document.getElementById(id);
    if (details instanceof HTMLDetailsElement) {
      details.open = false;
    }
  }
}

function applyExercisePayload(payload) {
  const exercise = payload.exercise;
  const dataset = payload.dataset;
  const eyebrow = document.getElementById("workspace-eyebrow");
  const title = document.getElementById("workspace-exercise-title");
  const prompt = document.getElementById("workspace-prompt-text");
  const outputRequirements = document.getElementById("workspace-output-requirements");
  const hint = document.getElementById("workspace-hint-text");
  const objectives = document.getElementById("workspace-objectives-list");
  const sampleSql = document.getElementById("workspace-sample-sql");
  const schemaPanel = document.getElementById("workspace-schema-panel");
  const schemaContent = document.getElementById("workspace-schema-content");
  const editorNote = document.querySelector(".workspace-editor-panel .placeholder-note");
  const timerRegion = document.getElementById("workspace-timer-region");
  const firstPassElapsed = document.getElementById("workspace-first-pass-elapsed");

  if (eyebrow instanceof HTMLElement) {
    eyebrow.textContent = `${dataset.name} · ${exercise.difficulty}`;
  }
  if (title instanceof HTMLElement) {
    title.textContent = exercise.title;
  }
  if (prompt instanceof HTMLElement) {
    prompt.textContent = exercise.prompt;
  }
  if (outputRequirements instanceof HTMLElement) {
    outputRequirements.textContent = exercise.output_requirements ?? "";
  }
  if (hint instanceof HTMLElement) {
    hint.textContent = exercise.hint;
  }
  if (objectives instanceof HTMLElement) {
    objectives.innerHTML = exercise.learning_objectives
      .map((objective) => `<li>${formatCell(objective)}</li>`)
      .join("");
  }
  if (sampleSql instanceof HTMLElement) {
    sampleSql.textContent = exercise.sample_sql ?? "";
  }
  const answerBlock = document.getElementById("workspace-answer-block");
  const answerSql = document.getElementById("workspace-answer-sql");
  if (answerBlock instanceof HTMLElement && answerSql instanceof HTMLElement) {
    const referenceSql = exercise.reference_sql ?? "";
    answerSql.textContent = referenceSql;
    answerBlock.hidden = !referenceSql;
  }
  if (schemaPanel instanceof HTMLElement && schemaContent instanceof HTMLElement) {
    const schemaHtml = renderSchemaHtml(payload.schema);
    schemaContent.innerHTML = schemaHtml;
    schemaPanel.hidden = !schemaHtml;
  }
  collapseContextDisclosures();
  if (editorNote instanceof HTMLElement) {
    editorNote.textContent = `Write PostgreSQL for: ${exercise.title}`;
  }
  if (timerRegion instanceof HTMLElement) {
    timerRegion.hidden = false;
  }
  if (firstPassElapsed instanceof HTMLElement) {
    if (payload.progress?.first_pass_elapsed) {
      firstPassElapsed.textContent = ` — solved in ${payload.progress.first_pass_elapsed}`;
      firstPassElapsed.hidden = false;
    } else {
      firstPassElapsed.textContent = "";
      firstPassElapsed.hidden = true;
    }
  }

  setEditorSql(payload.attempt?.sql ?? "");
  updateProgressUi(payload.progress);
  updateNavigationButtons(payload.navigation);
  document.title = `${exercise.title} - SQL Gym`;
}

function updateProgressUi(progress) {
  const passedCount = document.getElementById("workspace-passed-count");
  if (passedCount instanceof HTMLElement && progress?.passed_count !== undefined) {
    passedCount.textContent = String(progress.passed_count);
  }

  const badge = document.getElementById("workspace-progress-badge");
  if (badge instanceof HTMLElement && progress?.status) {
    // Prefer the server-provided label (single source of truth).
    badge.textContent = progress.label ?? progress.status;
    badge.className = `progress-badge progress-badge-${progress.status}`;
  }
}

function hasCoarsePointer() {
  return window.matchMedia("(pointer: coarse)").matches;
}

function createGradingModal(submitButton, nextNavButton) {
  const backdrop = document.getElementById("workspace-grading-modal");
  const title = document.getElementById("workspace-grading-title");
  const summary = document.getElementById("workspace-grading-summary");
  const okButton = document.getElementById("workspace-grading-ok");
  const nextButton = document.getElementById("workspace-grading-next");
  const workspaceShell = document.querySelector("[data-workspace-shell]");
  if (
    !(backdrop instanceof HTMLElement) ||
    !(title instanceof HTMLElement) ||
    !(summary instanceof HTMLElement) ||
    !(okButton instanceof HTMLButtonElement) ||
    !(nextButton instanceof HTMLButtonElement)
  ) {
    return {
      show() {},
      hide() {},
    };
  }

  if (backdrop.parentElement !== document.body) {
    document.body.appendChild(backdrop);
  }

  const isOpen = () => !backdrop.hidden;

  const canGoToNextExercise = (passed) =>
    passed &&
    nextNavButton instanceof HTMLButtonElement &&
    !nextNavButton.disabled &&
    Boolean(nextNavButton.dataset.targetUrl);

  const setShellInert = (inert) => {
    if (workspaceShell instanceof HTMLElement) {
      workspaceShell.inert = inert;
    }
  };

  const hide = () => {
    backdrop.hidden = true;
    nextButton.hidden = true;
    setShellInert(false);
    if (submitButton instanceof HTMLButtonElement) {
      submitButton.focus();
    }
  };

  const show = (grading) => {
    const passed = grading.passed === true;
    title.textContent = passed ? "Passed" : "Not yet correct";
    summary.textContent = grading.summary ?? "";
    summary.className = passed ? "feedback feedback-pass" : "feedback feedback-fail";
    const showNext = canGoToNextExercise(passed);
    nextButton.hidden = !showNext;
    backdrop.hidden = false;
    setShellInert(true);
    if (!hasCoarsePointer()) {
      if (showNext) {
        nextButton.focus();
      } else {
        okButton.focus();
      }
    }
  };

  const dismissFromBackdrop = (event) => {
    if (event.target === backdrop) {
      event.preventDefault();
      hide();
    }
  };

  okButton.addEventListener("click", (event) => {
    event.preventDefault();
    hide();
  });
  nextButton.addEventListener("click", (event) => {
    event.preventDefault();
    hide();
    if (nextNavButton instanceof HTMLButtonElement) {
      nextNavButton.click();
    }
  });
  backdrop.addEventListener("click", dismissFromBackdrop);
  backdrop.addEventListener("touchend", dismissFromBackdrop);
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && isOpen()) {
      hide();
    }
  });

  return { show, hide };
}

function initWorkspaceStopwatch({ onStop, initialElapsedSeconds = 0, stopped = false }) {
  const display = document.getElementById("timer-display");
  if (!(display instanceof HTMLElement)) {
    return { getElapsedSeconds: () => null, stop() {}, reset() {} };
  }

  let startedAtMs = Date.now() - initialElapsedSeconds * 1000;
  let frozenElapsedSeconds = null;
  let intervalId = null;
  let isStopped = stopped;

  const formatTime = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remainder = seconds % 60;
    return `${minutes}:${String(remainder).padStart(2, "0")}`;
  };

  const currentElapsedSeconds = () =>
    Math.max(0, Math.round((Date.now() - startedAtMs) / 1000));

  const renderElapsed = () => {
    const elapsed = currentElapsedSeconds();
    display.textContent = formatTime(elapsed);
    return elapsed;
  };

  const getElapsedSeconds = () => {
    if (frozenElapsedSeconds !== null) {
      return Math.max(1, frozenElapsedSeconds);
    }
    return Math.max(1, renderElapsed());
  };

  const stop = () => {
    if (isStopped) {
      return getElapsedSeconds();
    }
    isStopped = true;
    if (intervalId !== null) {
      window.clearInterval(intervalId);
      intervalId = null;
    }
    frozenElapsedSeconds = renderElapsed();
    onStop?.(frozenElapsedSeconds);
    return frozenElapsedSeconds;
  };

  const reset = ({ elapsedSeconds = 0, keepStopped = false } = {}) => {
    if (intervalId !== null) {
      window.clearInterval(intervalId);
      intervalId = null;
    }
    startedAtMs = Date.now() - elapsedSeconds * 1000;
    isStopped = keepStopped;
    frozenElapsedSeconds = keepStopped ? elapsedSeconds : null;
    display.textContent = formatTime(elapsedSeconds);
    if (!isStopped) {
      intervalId = window.setInterval(renderElapsed, 1000);
    }
  };

  reset({ elapsedSeconds: initialElapsedSeconds, keepStopped: stopped });
  return { getElapsedSeconds, stop, reset };
}

function initWorkspaceNavigation({
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

function parseElapsedDisplay(value) {
  if (!value || typeof value !== "string") {
    return 0;
  }
  const match = value.match(/^(\d+):(\d{2})$/);
  if (!match) {
    return 0;
  }
  return Number.parseInt(match[1], 10) * 60 + Number.parseInt(match[2], 10);
}

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

  const modal = createGradingModal(submitButton, document.getElementById("workspace-next"));
  let runInFlight = false;
  let submitInFlight = false;
  const initialProgress = workspaceConfig.progress ?? {};
  const alreadyPassed = initialProgress.status === "passed";
  const initialElapsedSeconds = parseElapsedDisplay(initialProgress.first_pass_elapsed);
  let stopwatch = initWorkspaceStopwatch({
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
          const minutes = Math.floor(elapsedSeconds / 60);
          const remainder = elapsedSeconds % 60;
          firstPassElapsed.textContent = ` — solved in ${minutes}:${String(remainder).padStart(2, "0")}`;
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
