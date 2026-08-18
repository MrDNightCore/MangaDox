// Form handlers and confirm dialogs
// Runs on page load to attach event listeners to forms and selects

document.addEventListener("DOMContentLoaded", function () {
  // Auto-submit selects (for status, type, sort filters, chapter select, etc.)
  document
    .querySelectorAll('select[data-auto-submit="true"]')
    .forEach(function (select) {
      select.addEventListener("change", function () {
        this.form.submit();
      });
    });

  // Chapter select navigation
  var chapterSelect = document.getElementById("chapter-select");
  if (chapterSelect) {
    chapterSelect.addEventListener("change", function () {
      if (this.value) {
        window.location.href = this.value;
      }
    });
  }

  // Genre filter checkbox
  document
    .querySelectorAll('input[name="genre_cb"]')
    .forEach(function (checkbox) {
      checkbox.addEventListener("change", function () {
        updateGenreFilter();
      });
    });

  // Forms with confirm dialogs
  document.querySelectorAll("form[data-confirm]").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      var confirmMsg = this.getAttribute("data-confirm");
      if (!confirm(confirmMsg)) {
        e.preventDefault();
      }
    });
  });

  // Message dismiss buttons
  document.querySelectorAll(".msg-dismiss").forEach(function (btn) {
    btn.addEventListener("click", function () {
      this.parentElement.remove();
    });
  });

  // Admin sidebar mobile toggle
  var adminSidebar = document.getElementById("admin-sidebar");
  if (adminSidebar) {
    document
      .querySelectorAll(".mobile-toggle.admin-toggle")
      .forEach(function (btn) {
        btn.addEventListener("click", function () {
          adminSidebar.classList.toggle("open");
        });
      });
  }
});

// Genre filter function (moved from inline script in manga_list.html)
function updateGenreFilter() {
  var checked = document.querySelectorAll('input[name="genre_cb"]:checked');
  var slugs = Array.from(checked).map(function (c) {
    return c.value;
  });
  document.getElementById("genre-hidden").value = slugs.join(",");
  document.getElementById("browse-form").submit();
}

// Delete image function (for chapter_form.html)
function deleteImage(imgId) {
  var imgElement = document.getElementById("image-" + imgId);
  if (imgElement) {
    imgElement.remove();
  }
}
