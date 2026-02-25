document.addEventListener("DOMContentLoaded", function () {
  const items = Array.from(document.querySelectorAll(".messages li"));
  if (!items.length) return;

  // helper: normalize message text (lowercase, remove punctuation)
  const normalize = (s) =>
    s
      .replace(/[^a-z0-9\s]/gi, "")
      .toLowerCase()
      .trim();

  const normalized = items.map((li) => ({
    el: li,
    text: normalize(li.textContent || ""),
  }));

  const logoutItemObj = normalized.find((o) =>
    o.text.includes("logged out successfully"),
  );

  if (logoutItemObj) {
    // If logout present, remove everything except the logout message
    normalized.forEach((o) => {
      if (o.el !== logoutItemObj.el) o.el.remove();
    });

    // Trigger reflow so CSS animation runs
    requestAnimationFrame(() => {
      void logoutItemObj.el.offsetWidth;
    });

    // Auto-dismiss after visibleMs
    const visibleMs = 3000;
    const fadeFallbackMs = 900;
    setTimeout(() => {
      logoutItemObj.el.classList.add("fade-out");
      const handleRemove = () => {
        logoutItemObj.el.removeEventListener("transitionend", handleRemove);
        if (logoutItemObj.el.parentNode)
          logoutItemObj.el.parentNode.removeChild(logoutItemObj.el);
      };
      logoutItemObj.el.addEventListener("transitionend", handleRemove);
      setTimeout(() => {
        if (logoutItemObj.el.parentNode)
          logoutItemObj.el.parentNode.removeChild(logoutItemObj.el);
      }, fadeFallbackMs + 200);
    }, visibleMs);
    // Attach close handler to the close button if present
    const closeBtn = logoutItemObj.el.querySelector(".msg-close");
    if (closeBtn) {
      closeBtn.addEventListener("click", () => {
        // immediate fade and remove
        logoutItemObj.el.classList.add("fade-out");
        setTimeout(() => {
          if (logoutItemObj.el.parentNode)
            logoutItemObj.el.parentNode.removeChild(logoutItemObj.el);
        }, 500);
      });
    }
  } else {
    // No logout message — remove any "welcome back" lines (stale welcome messages)
    normalized.forEach((o) => {
      if (o.text.includes("welcome back")) {
        o.el.remove();
      }
    });

    // Ensure remaining messages animate
    requestAnimationFrame(() => {
      document.querySelectorAll(".messages li").forEach((el) => {
        void el.offsetWidth;
      });
    });
  }

  // For any remaining messages add close-button handlers (manual dismiss)
  document.querySelectorAll(".messages li .msg-close").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      const li = e.target.closest("li");
      if (!li) return;
      li.classList.add("fade-out");
      setTimeout(() => {
        if (li.parentNode) li.parentNode.removeChild(li);
      }, 500);
    });
  });
});
