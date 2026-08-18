// Image error handler - replace broken images with default placeholder
document.addEventListener("DOMContentLoaded", function () {
  document
    .querySelectorAll("img[data-onerror-fallback]")
    .forEach(function (img) {
      img.addEventListener("error", function () {
        if (!this.hasAttribute("data-error-handled")) {
          this.setAttribute("data-error-handled", "true");
          this.src = this.getAttribute("data-onerror-fallback");
        }
      });
    });
});
