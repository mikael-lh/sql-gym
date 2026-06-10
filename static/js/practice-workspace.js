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

function createGradingModal(submitButton) {
  const backdrop = document.getElementById("workspace-grading-modal");
  const title = document.getElementById("workspace-grading-title");
  const summary = document.getElementById("workspace-grading-summary");
  const okButton = document.getElementById("workspace-grading-ok");
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

  const hide = () => {
    backdrop.hidden = true;
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
    okButton.focus();
  };

  okButton.addEventListener("click", hide);
  backdrop.addEventListener("click", (event) => {
    if (event.target === backdrop) {
      hide();
    }
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !backdrop.hidden) {
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

  return { getElapsedSeconds };
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

  renderConsoleAttempt(consoleEl, config.attempt);

  const modal = createGradingModal(submitButton);
  let runInFlight = false;
  let submitInFlight = false;
  let timer = { getElapsedSeconds: () => null };

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
      const response = await fetch(buildSubmitUrl(config), {
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
      const response = await fetch(buildRunUrl(config), {
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
      } finally {
        clearButton.disabled = false;
      }
    });
  }

  return { hideGradingModal: modal.hide };
}
