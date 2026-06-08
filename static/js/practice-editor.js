document.addEventListener("DOMContentLoaded", () => {
  const config = document.getElementById("practice-editor-config");
  if (!config || typeof globalThis.initPracticeEditor !== "function") {
    return;
  }

  const hiddenInput = document.getElementById(config.dataset.inputId);
  const initialSql =
    hiddenInput instanceof HTMLTextAreaElement || hiddenInput instanceof HTMLInputElement
      ? hiddenInput.value
      : "";

  globalThis.initPracticeEditor(config.dataset.hostId, config.dataset.inputId, initialSql);
});
