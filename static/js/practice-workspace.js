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

export function initPracticeWorkspace() {
  const config = readWorkspaceConfig();
  const consoleEl = document.getElementById("workspace-console");
  const runButton = document.getElementById("workspace-run-sql");
  if (!config || !(consoleEl instanceof HTMLElement) || !(runButton instanceof HTMLButtonElement)) {
    return;
  }

  renderConsoleAttempt(consoleEl, config.attempt);

  let runInFlight = false;

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
}
