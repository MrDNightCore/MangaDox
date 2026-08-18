// Chapter form delete image handler
document.addEventListener("DOMContentLoaded", function () {
  // Attach delete handlers to preview delete buttons
  document.querySelectorAll(".preview-delete").forEach(function (btn) {
    btn.addEventListener("click", function (e) {
      e.preventDefault();
      var imgDiv = this.closest(".preview-item");
      if (!imgDiv) return;

      var imgId = imgDiv.id.replace("img-", "");
      if (!imgId) return;

      if (!confirm("Delete this page image?")) return;

      // CSRF token from Django template
      var csrfToken = document.querySelector('[name="csrfmiddlewaretoken"]')
        ? document.querySelector('[name="csrfmiddlewaretoken"]').value
        : "";

      fetch("/panel/chapter-image/" + imgId + "/delete/", {
        method: "POST",
        headers: {
          "X-CSRFToken": csrfToken,
          "Content-Type": "application/json",
        },
      })
        .then(function (r) {
          return r.json();
        })
        .then(function (d) {
          if (d.success) {
            imgDiv.remove();
          } else {
            alert("Failed to delete image");
          }
        })
        .catch(function (error) {
          console.error("Delete error:", error);
          alert("Error deleting image");
        });
    });
  });
});
