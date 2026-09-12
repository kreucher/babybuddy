/* Live elapsed time for purpose-specific breastfeeding timers. */
(function () {
  function updateElapsedTimers() {
    document
      .querySelectorAll("[data-breastfeeding-start]")
      .forEach(function (element) {
        var start = new Date(element.dataset.breastfeedingStart);
        var seconds = Math.max(
          0,
          Math.floor((Date.now() - start.getTime()) / 1000),
        );
        var hours = Math.floor(seconds / 3600);
        var minutes = Math.floor((seconds % 3600) / 60);
        var remainingSeconds = seconds % 60;
        var parts = [minutes, remainingSeconds].map(function (part) {
          return String(part).padStart(2, "0");
        });
        if (hours > 0) {
          parts.unshift(String(hours));
        }
        element.textContent = parts.join(":");
        element
          .closest(".card, .alert")
          .classList.toggle("breastfeeding-stale", seconds >= 5400);
      });
  }

  document.addEventListener("DOMContentLoaded", function () {
    updateElapsedTimers();
    window.setInterval(updateElapsedTimers, 1000);
  });
  document.addEventListener("visibilitychange", function () {
    if (!document.hidden) {
      updateElapsedTimers();
    }
  });
})();
