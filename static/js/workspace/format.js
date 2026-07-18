/** Shared M:SS formatting and HTML-safe cell text. */

export function formatTime(seconds) {
  const minutes = Math.floor(seconds / 60);
  const remainder = seconds % 60;
  return `${minutes}:${String(remainder).padStart(2, "0")}`;
}

export function parseElapsedDisplay(value) {
  if (!value || typeof value !== "string") {
    return 0;
  }
  const match = value.match(/^(\d+):(\d{2})$/);
  if (!match) {
    return 0;
  }
  return Number.parseInt(match[1], 10) * 60 + Number.parseInt(match[2], 10);
}

export function formatCell(cell) {
  if (cell === null || cell === undefined) {
    return '<span class="null-cell">NULL</span>';
  }
  return String(cell)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}
