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

const config = readWorkspaceConfig();
if (config) {
  document.documentElement.dataset.workspaceReady = "shell";
}
