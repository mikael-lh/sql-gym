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
    <p class="eyebrow">Execution</p>
    <h3>Query result</h3>
    ${truncatedNote}
    <p class="catalog-count">${result.row_count} ${rowLabel} returned.</p>
    <div class="result-table-wrap">
      <table class="result-table">
        <thead><tr>${header}</tr></thead>
        <tbody>${body}</tbody>
      </table>
    </div>
  `;
}

function renderExecutionError(consoleEl, error) {
  consoleEl.innerHTML = `
    <p class="eyebrow">Execution</p>
    <h3>Could not run query</h3>
    <p class="feedback feedback-error">${formatCell(error.message)}</p>
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
  if (filters?.mode) {
    params.set("mode", filters.mode);
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
      mode: params.get("mode") ?? "",
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
  const footerPosition = document.getElementById("workspace-footer-position");
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

function applyExercisePayload(payload) {
  const exercise = payload.exercise;
  const dataset = payload.dataset;
  const eyebrow = document.getElementById("workspace-eyebrow");
  const title = document.getElementById("workspace-exercise-title");
  const prompt = document.getElementById("workspace-prompt-text");
  const hint = document.getElementById("workspace-hint-text");
  const objectives = document.getElementById("workspace-objectives-list");
  const sampleSql = document.getElementById("workspace-sample-sql");
  const schemaPanel = document.getElementById("workspace-schema-panel");
  const schemaContent = document.getElementById("workspace-schema-content");
  const editorNote = document.querySelector(".workspace-editor-panel .placeholder-note");
  const timerRegion = document.getElementById("workspace-timer-region");
  const timerConfig = document.getElementById("practice-timer-config");
  const bestElapsed = document.getElementById("workspace-best-elapsed");

  if (eyebrow instanceof HTMLElement) {
    eyebrow.textContent = `${dataset.name} · ${exercise.difficulty} · ${exercise.mode}`;
  }
  if (title instanceof HTMLElement) {
    title.textContent = exercise.title;
  }
  if (prompt instanceof HTMLElement) {
    prompt.textContent = exercise.prompt;
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
  if (schemaPanel instanceof HTMLElement && schemaContent instanceof HTMLElement) {
    const schemaHtml = renderSchemaHtml(payload.schema);
    schemaContent.innerHTML = schemaHtml;
    schemaPanel.hidden = !schemaHtml;
  }
  if (editorNote instanceof HTMLElement) {
    editorNote.textContent = `Write PostgreSQL for: ${exercise.title}`;
  }
  if (timerRegion instanceof HTMLElement && timerConfig instanceof HTMLElement) {
    const isTimed = exercise.mode === "Timed";
    timerRegion.hidden = !isTimed;
    if (isTimed) {
      timerConfig.dataset.durationSeconds = String(exercise.estimated_time_minutes * 60);
    }
  }
  if (bestElapsed instanceof HTMLElement) {
    bestElapsed.textContent = payload.progress?.best_elapsed
      ? ` — best time ${payload.progress.best_elapsed}`
      : "";
  }

  setEditorSql(payload.attempt?.sql ?? "");
  updateProgressUi(payload.progress);
  updateNavigationButtons(payload.navigation);
  document.title = `${exercise.title} - SQL Gym`;
}

function progressLabelForStatus(status) {
  if (status === "passed") {
    return "Passed";
  }
  if (status === "attempted") {
    return "Attempted";
  }
  return "Not started";
}

function updateProgressUi(progress) {
  const passedCount = document.getElementById("workspace-passed-count");
  if (passedCount instanceof HTMLElement && progress?.passed_count !== undefined) {
    passedCount.textContent = String(progress.passed_count);
  }

  const badge = document.getElementById("workspace-progress-badge");
  if (badge instanceof HTMLElement && progress?.status) {
    badge.textContent = progress.label ?? progressLabelForStatus(progress.status);
    badge.className = `progress-badge progress-badge-${progress.status}`;
  }
}

function prefersReducedPointerFocus() {
  return window.matchMedia("(pointer: coarse)").matches;
}

function createGradingModal(submitButton) {
  const backdrop = document.getElementById("workspace-grading-modal");
  const title = document.getElementById("workspace-grading-title");
  const summary = document.getElementById("workspace-grading-summary");
  const okButton = document.getElementById("workspace-grading-ok");
  const workspaceShell = document.querySelector("[data-workspace-shell]");
  if (
    !(backdrop instanceof HTMLElement) ||
    !(title instanceof HTMLElement) ||
    !(summary instanceof HTMLElement) ||
    !(okButton instanceof HTMLButtonElement)
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

  const setShellInert = (inert) => {
    if (workspaceShell instanceof HTMLElement) {
      workspaceShell.inert = inert;
    }
  };

  const hide = () => {
    backdrop.hidden = true;
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
    backdrop.hidden = false;
    setShellInert(true);
    if (!prefersReducedPointerFocus()) {
      okButton.focus();
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
  backdrop.addEventListener("click", dismissFromBackdrop);
  backdrop.addEventListener("touchend", dismissFromBackdrop);
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && isOpen()) {
      hide();
    }
  });

  return { show, hide };
}

function initWorkspaceTimer(onTimeoutSubmit) {
  const config = document.getElementById("practice-timer-config");
  const startButton = document.getElementById("start-timed-exercise");
  const display = document.getElementById("timer-display");
  if (
    !(config instanceof HTMLElement) ||
    !(startButton instanceof HTMLButtonElement) ||
    !(display instanceof HTMLElement)
  ) {
    return { getElapsedSeconds: () => null };
  }

  const totalSeconds = Number.parseInt(config.dataset.durationSeconds ?? "", 10);
  if (!Number.isFinite(totalSeconds) || totalSeconds <= 0) {
    return { getElapsedSeconds: () => null };
  }

  let remainingSeconds = totalSeconds;
  let startedAtMs = null;
  let intervalId = null;

  const formatTime = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remainder = seconds % 60;
    return `${minutes}:${String(remainder).padStart(2, "0")}`;
  };

  const getElapsedSeconds = () => {
    if (startedAtMs === null) {
      return null;
    }
    const elapsed = Math.max(1, Math.round((Date.now() - startedAtMs) / 1000));
    return Math.min(elapsed, totalSeconds);
  };

  const tick = () => {
    remainingSeconds -= 1;
    if (remainingSeconds <= 0) {
      display.textContent = "0:00";
      window.clearInterval(intervalId);
      intervalId = null;
      onTimeoutSubmit();
      return;
    }
    display.textContent = formatTime(remainingSeconds);
  };

  startButton.addEventListener("click", () => {
    if (intervalId !== null) {
      return;
    }
    startedAtMs = Date.now();
    remainingSeconds = totalSeconds;
    startButton.hidden = true;
    display.hidden = false;
    display.textContent = formatTime(remainingSeconds);
    intervalId = window.setInterval(tick, 1000);
  });

  const reset = () => {
    if (intervalId !== null) {
      window.clearInterval(intervalId);
      intervalId = null;
    }
    startedAtMs = null;
    remainingSeconds = Number.parseInt(config.dataset.durationSeconds ?? "", 10);
    startButton.hidden = false;
    display.hidden = true;
    display.textContent = "";
  };

  return { getElapsedSeconds, reset };
}

function initWorkspaceNavigation({
  workspaceConfig,
  consoleEl,
  modal,
  timer,
  loadDrawerExercises,
}) {
  const drawer = document.getElementById("workspace-drawer");
  const drawerToggle = document.getElementById("workspace-drawer-toggle");
  const drawerClose = document.getElementById("workspace-drawer-close");
  const drawerList = document.getElementById("workspace-drawer-list");
  const prevButton = document.getElementById("workspace-prev");
  const nextButton = document.getElementById("workspace-next");
  const difficultyFilter = document.getElementById("workspace-filter-difficulty");
  const modeFilter = document.getElementById("workspace-filter-mode");

  const setDrawerOpen = (open) => {
    if (!(drawer instanceof HTMLElement) || !(drawerToggle instanceof HTMLButtonElement)) {
      return;
    }
    drawer.hidden = !open;
    drawerToggle.setAttribute("aria-expanded", open ? "true" : "false");
  };

  const loadExercise = async (datasetId, exerciseId, filters, { push = true } = {}) => {
    modal.hide();
    timer.reset();
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
    if (push) {
      window.history.pushState(
        { workspace: true },
        "",
        buildExercisePath(datasetId, exerciseId, filters),
      );
    }
    void loadDrawerExercises();
  };

  const navigateByPath = async (path) => {
    const url = new URL(path, window.location.origin);
    const parsed = parseExerciseLocation(url.pathname, url.search);
    if (!parsed) {
      return;
    }
    await loadExercise(parsed.dataset_id, parsed.exercise_id, parsed.filters, { push: false });
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
      void navigateByPath(targetUrl);
    });
  };
  wireNavButton(prevButton);
  wireNavButton(nextButton);

  const redirectForFilters = () => {
    const params = new URLSearchParams();
    if (difficultyFilter instanceof HTMLSelectElement && difficultyFilter.value) {
      params.set("difficulty", difficultyFilter.value);
    }
    if (modeFilter instanceof HTMLSelectElement && modeFilter.value) {
      params.set("mode", modeFilter.value);
    }
    const query = params.toString();
    window.location.assign(query ? `/practice?${query}` : "/practice");
  };
  if (difficultyFilter instanceof HTMLSelectElement) {
    difficultyFilter.addEventListener("change", redirectForFilters);
  }
  if (modeFilter instanceof HTMLSelectElement) {
    modeFilter.addEventListener("change", redirectForFilters);
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

  const modal = createGradingModal(submitButton);
  let runInFlight = false;
  let submitInFlight = false;
  let timer = { getElapsedSeconds: () => null, reset() {} };

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
    const elapsedSeconds = timer.getElapsedSeconds();
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
      if (payload.grading) {
        modal.show(payload.grading);
      }
      if (payload.progress) {
        updateProgressUi({
          passed_count: payload.progress.passed_count,
          status: payload.grading?.passed ? "passed" : "attempted",
          label: payload.grading?.passed ? "Passed" : "Attempted",
        });
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

  timer = initWorkspaceTimer(() => {
    void submitForGrading();
  });

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

  const loadDrawerExercises = async () => {
    const drawerList = document.getElementById("workspace-drawer-list");
    const drawerCount = document.getElementById("workspace-drawer-count");
    if (!(drawerList instanceof HTMLElement)) {
      return;
    }
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
        updateProgressUi({
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
    timer,
    loadDrawerExercises,
  });

  return { hideGradingModal: modal.hide };
}
