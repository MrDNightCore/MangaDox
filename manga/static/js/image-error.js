// Image error handler — swaps broken images for their declared fallback.
//
// Inline `onerror=""` attributes cannot be used because the Content Security
// Policy (script-src 'self') blocks inline event handlers, so every fallback
// is declared with `data-onerror-fallback` and wired up from here.
(function () {
  "use strict";

  var FALLBACK_ATTR = "data-onerror-fallback";
  var HANDLED_ATTR = "data-error-handled";

  function applyFallback(img) {
    if (!img || img.tagName !== "IMG" || img.hasAttribute(HANDLED_ATTR)) return;

    var fallback = img.getAttribute(FALLBACK_ATTR);
    if (!fallback || img.getAttribute("src") === fallback) return;

    img.setAttribute(HANDLED_ATTR, "true");
    // Lazy loading would defer the replacement of an already visible image.
    img.removeAttribute("loading");
    img.src = fallback;
  }

  function isBroken(img) {
    // `complete` stays false for lazy images that have not started loading,
    // so this only matches images that finished loading with no pixels.
    return img.complete && img.naturalWidth === 0;
  }

  // `error` does not bubble, so listen in the capture phase on the document.
  // This also covers images inserted later (e.g. search results).
  document.addEventListener(
    "error",
    function (event) {
      var target = event.target;
      if (target && target.tagName === "IMG" && target.hasAttribute(FALLBACK_ATTR)) {
        applyFallback(target);
      }
    },
    true
  );

  // Images can fail before this deferred script runs — sweep for those.
  function sweep() {
    var images = document.querySelectorAll("img[" + FALLBACK_ATTR + "]");
    Array.prototype.forEach.call(images, function (img) {
      if (isBroken(img)) applyFallback(img);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", sweep);
  } else {
    sweep();
  }
  window.addEventListener("load", sweep);
})();
