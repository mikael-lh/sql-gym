document.addEventListener("DOMContentLoaded", () => {
  const config = document.getElementById("practice-timer-config");
  const form = document.querySelector(".editor-form");
  const submitButton = form?.querySelector('button[formaction$="/submit"]');
  const elapsedInput = document.getElementById("elapsed-seconds-input");
  const startButton = document.getElementById("start-timed-exercise");
  const display = document.getElementById("timer-display");

  if (!config || !form || !submitButton || !elapsedInput || !startButton || !display) {
    return;
  }

  const totalSeconds = Number.parseInt(config.dataset.durationSeconds ?? "", 10);
  if (!Number.isFinite(totalSeconds) || totalSeconds <= 0) {
    return;
  }

  let remainingSeconds = totalSeconds;
  let startedAtMs = null;
  let intervalId = null;
  let submitting = false;

  const formatTime = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remainder = seconds % 60;
    return `${minutes}:${String(remainder).padStart(2, "0")}`;
  };

  const setElapsedOnSubmit = () => {
    if (startedAtMs === null) {
      return;
    }
    const elapsed = Math.max(1, Math.round((Date.now() - startedAtMs) / 1000));
    elapsedInput.value = String(Math.min(elapsed, totalSeconds));
  };

  const submitForGrading = () => {
    if (submitting) {
      return;
    }
    submitting = true;
    setElapsedOnSubmit();
    submitButton.click();
  };

  const tick = () => {
    remainingSeconds -= 1;
    if (remainingSeconds <= 0) {
      display.textContent = "0:00";
      window.clearInterval(intervalId);
      intervalId = null;
      submitForGrading();
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

  submitButton.addEventListener("click", () => {
    setElapsedOnSubmit();
  });
});
