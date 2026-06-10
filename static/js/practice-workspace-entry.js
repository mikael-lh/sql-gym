import { initPracticeWorkspace } from "./practice-workspace.js";

document.addEventListener("DOMContentLoaded", () => {
  initPracticeWorkspace();
  document.documentElement.dataset.workspaceReady = "submit";
});
