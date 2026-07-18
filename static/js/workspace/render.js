import { formatCell } from "./format.js";
import { getSqlInput } from "./api-client.js";

export function renderQueryResult(consoleEl, result) {
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

export function renderExecutionError(consoleEl, error) {
  consoleEl.innerHTML = `
    <div class="workspace-console-meta">
      <p class="eyebrow">Execution</p>
      <h3>Could not run query</h3>
      <p class="feedback feedback-error">${formatCell(error.message)}</p>
    </div>
  `;
}

export function renderConsoleAttempt(consoleEl, attempt) {
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

export function updateNavigationButtons(navigation) {
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

export function updateProgressUi(progress) {
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

export function applyExercisePayload(payload) {
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

function hasCoarsePointer() {
  return window.matchMedia("(pointer: coarse)").matches;
}

export function createGradingModal(submitButton, nextNavButton) {
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
