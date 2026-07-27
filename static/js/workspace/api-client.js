/** Practice API URL helpers and workspace config reading. */

export function readWorkspaceConfig() {
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

export function getSqlInput() {
  const input = document.getElementById("practice-sql-input");
  if (input instanceof HTMLTextAreaElement || input instanceof HTMLInputElement) {
    return input;
  }
  return null;
}

export function buildRunUrl(config) {
  return `/api/practice/${config.dataset_id}/${config.exercise_id}/run`;
}

export function buildSubmitUrl(config) {
  return `/api/practice/${config.dataset_id}/${config.exercise_id}/submit`;
}

export function buildExplainUrl(config) {
  return `/api/practice/${config.dataset_id}/${config.exercise_id}/explain`;
}

function filtersToQuery(filters) {
  const params = new URLSearchParams();
  if (filters?.difficulty) {
    params.set("difficulty", filters.difficulty);
  }
  const query = params.toString();
  return query ? `?${query}` : "";
}

export function buildExercisePath(datasetId, exerciseId, filters) {
  return `/practice/${datasetId}/${exerciseId}${filtersToQuery(filters)}`;
}

export function buildExerciseApiUrl(datasetId, exerciseId, filters) {
  return `/api/practice/${datasetId}/${exerciseId}${filtersToQuery(filters)}`;
}

export function buildExercisesListUrl(filters) {
  return `/api/practice/exercises${filtersToQuery(filters)}`;
}

export function parseExerciseLocation(pathname, search) {
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
