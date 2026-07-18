import { formatTime } from "./format.js";

export function initWorkspaceStopwatch({
  onStop,
  initialElapsedSeconds = 0,
  stopped = false,
}) {
  const display = document.getElementById("timer-display");
  if (!(display instanceof HTMLElement)) {
    return { getElapsedSeconds: () => null, stop() {}, reset() {} };
  }

  let startedAtMs = Date.now() - initialElapsedSeconds * 1000;
  let frozenElapsedSeconds = null;
  let intervalId = null;
  let isStopped = stopped;

  const currentElapsedSeconds = () =>
    Math.max(0, Math.round((Date.now() - startedAtMs) / 1000));

  const renderElapsed = () => {
    const elapsed = currentElapsedSeconds();
    display.textContent = formatTime(elapsed);
    return elapsed;
  };

  const getElapsedSeconds = () => {
    if (frozenElapsedSeconds !== null) {
      return Math.max(1, frozenElapsedSeconds);
    }
    return Math.max(1, renderElapsed());
  };

  const stop = () => {
    if (isStopped) {
      return getElapsedSeconds();
    }
    isStopped = true;
    if (intervalId !== null) {
      window.clearInterval(intervalId);
      intervalId = null;
    }
    frozenElapsedSeconds = renderElapsed();
    onStop?.(frozenElapsedSeconds);
    return frozenElapsedSeconds;
  };

  const reset = ({ elapsedSeconds = 0, keepStopped = false } = {}) => {
    if (intervalId !== null) {
      window.clearInterval(intervalId);
      intervalId = null;
    }
    startedAtMs = Date.now() - elapsedSeconds * 1000;
    isStopped = keepStopped;
    frozenElapsedSeconds = keepStopped ? elapsedSeconds : null;
    display.textContent = formatTime(elapsedSeconds);
    if (!isStopped) {
      intervalId = window.setInterval(renderElapsed, 1000);
    }
  };

  reset({ elapsedSeconds: initialElapsedSeconds, keepStopped: stopped });
  return { getElapsedSeconds, stop, reset };
}
