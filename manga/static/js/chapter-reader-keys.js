// Chapter reader keyboard navigation
document.addEventListener("DOMContentLoaded", function () {
  document.addEventListener("keydown", function (e) {
    if (e.key === "ArrowLeft") {
      var p = document.getElementById("prev-btn");
      if (p && !p.classList.contains("disabled")) {
        p.click();
      }
    }
    if (e.key === "ArrowRight") {
      var n = document.getElementById("next-btn");
      if (n && !n.classList.contains("disabled")) {
        n.click();
      }
    }
  });
});
