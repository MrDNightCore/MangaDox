/* MangaDox — Main JavaScript */
(function () {
  "use strict";

  // ---- Mobile nav toggle ----
  var mobileBtn = document.getElementById("mobile-toggle");
  var mainNav = document.getElementById("main-nav");
  if (mobileBtn && mainNav) {
    mobileBtn.addEventListener("click", function () {
      mainNav.classList.toggle("open");
    });
  }

  // ---- User dropdown ----
  var userBtn = document.getElementById("user-menu-btn");
  var userDrop = document.getElementById("user-dropdown");
  if (userBtn && userDrop) {
    userBtn.addEventListener("click", function (e) {
      e.stopPropagation();
      userDrop.classList.toggle("open");
    });
    document.addEventListener("click", function () {
      userDrop.classList.remove("open");
    });
  }

  // ---- Theme toggle ----
  // Initialize theme from localStorage first (before button setup)
  (function initTheme() {
    try {
      var root = document.documentElement;
      var stored = localStorage.getItem("manga_theme");
      var themeToSet = stored || "dark";

      // Set initial theme
      root.setAttribute("data-theme", themeToSet);
      console.log("Theme initialized to:", themeToSet);
    } catch (e) {
      console.error("Theme init error:", e);
      document.documentElement.setAttribute("data-theme", "dark");
    }
  })();

  var themeBtn = document.getElementById("theme-toggle");
  if (themeBtn) {
    function updateIcon() {
      var icon = themeBtn.querySelector("i");
      if (!icon) return;
      var current =
        document.documentElement.getAttribute("data-theme") || "dark";
      var isLight = current === "light";

      // Set icon based on current theme
      icon.className = isLight ? "fas fa-sun" : "fas fa-moon";
      themeBtn.title = isLight ? "Switch to dark mode" : "Switch to light mode";
      console.log("Icon updated for theme:", current);
    }

    // Update icon on load
    updateIcon();

    // Click handler with explicit theme toggle
    var toggleTheme = function (e) {
      e.preventDefault();
      var root = document.documentElement;
      var current = root.getAttribute("data-theme") || "dark";
      var nextTheme = current === "light" ? "dark" : "light";

      // Set new theme
      root.setAttribute("data-theme", nextTheme);

      // Save to localStorage
      try {
        localStorage.setItem("manga_theme", nextTheme);
      } catch (err) {
        console.error("localStorage error:", err);
      }

      // Update icon
      updateIcon();
      console.log("Theme toggled to:", nextTheme);
    };

    themeBtn.addEventListener("click", toggleTheme);
    themeBtn.addEventListener("keydown", function (e) {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        toggleTheme(e);
      }
    });
  } else {
    console.warn("Theme button not found");
  }

  // ---- Quick search ----
  var searchInput = document.getElementById("quick-search");
  var searchResults = document.getElementById("search-results");
  var searchTimer = null;
  if (searchInput && searchResults) {
    searchInput.addEventListener("input", function () {
      clearTimeout(searchTimer);
      var q = searchInput.value.trim();
      if (q.length < 2) {
        searchResults.classList.remove("open");
        return;
      }
      searchTimer = setTimeout(function () {
        fetch("/api/search/?q=" + encodeURIComponent(q))
          .then(function (r) {
            return r.json();
          })
          .then(function (d) {
            if (!d.results || d.results.length === 0) {
              searchResults.innerHTML =
                '<div class="search-no-results">No results found</div>';
              searchResults.classList.add("open");
              return;
            }
            var html = "";
            d.results.forEach(function (m) {
              html +=
                '<a class="search-result-item" href="/manga/' +
                m.slug +
                '/">' +
                '<img src="' +
                m.cover +
                '" alt="">' +
                "<div><h4>" +
                m.title +
                "</h4><span>" +
                m.manga_type +
                " · Ch. " +
                m.latest_chapter +
                "</span></div>" +
                "</a>";
            });
            searchResults.innerHTML = html;
            searchResults.classList.add("open");
          });
      }, 300);
    });
    document.addEventListener("click", function (e) {
      if (!e.target.closest("#search-box"))
        searchResults.classList.remove("open");
    });
  }
})();
