// Manga detail page functionality: tabs, bookmarks, comments, ratings

document.addEventListener("DOMContentLoaded", function () {
  // Tabs
  document.querySelectorAll(".tab-btn").forEach(function (btn) {
    btn.addEventListener("click", function () {
      document.querySelectorAll(".tab-btn").forEach(function (b) {
        b.classList.remove("active");
      });
      document.querySelectorAll(".tab-panel").forEach(function (p) {
        p.classList.remove("active");
      });
      btn.classList.add("active");
      var tabPanel = document.getElementById("tab-" + btn.dataset.tab);
      if (tabPanel) tabPanel.classList.add("active");
    });
  });

  // Bookmark
  var bmBtn = document.getElementById("bookmark-btn");
  if (bmBtn) {
    bmBtn.addEventListener("click", function () {
      var csrfToken = document.querySelector("[name=csrfmiddlewaretoken]")
        ? document.querySelector("[name=csrfmiddlewaretoken]").value
        : "";
      fetch("/manga/toggle-bookmark/", {
        method: "POST",
        headers: {
          "X-CSRFToken": csrfToken,
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: "manga_id=" + bmBtn.dataset.manga,
      })
        .then(function (r) {
          return r.json();
        })
        .then(function (d) {
          if (d.error) {
            alert(d.error);
            return;
          }
          bmBtn.dataset.bookmarked = d.bookmarked;
          bmBtn.querySelector("i").className = d.bookmarked
            ? "fas fa-bookmark"
            : "far fa-bookmark";
          bmBtn.querySelector("span").textContent = d.bookmarked
            ? "Bookmarked"
            : "Bookmark";
          var bmCount = document.getElementById("bm-count");
          if (bmCount) bmCount.textContent = d.count;
        });
    });
  }

  // Comment form
  var cf = document.getElementById("comment-form");
  if (cf) {
    cf.addEventListener("submit", function (e) {
      e.preventDefault();
      var fd = new FormData(cf);
      var csrfToken = fd.get("csrfmiddlewaretoken");
      fetch("/manga/add-comment/", {
        method: "POST",
        headers: {
          "X-CSRFToken": csrfToken,
        },
        body: fd,
      })
        .then(function (r) {
          return r.json();
        })
        .then(function (d) {
          if (d.error) {
            alert(d.error);
            return;
          }
          var nc = document.getElementById("no-comments");
          if (nc) nc.remove();
          var div = document.createElement("div");
          div.className = "comment-item";
          div.innerHTML =
            '<div class="comment-header"><i class="fas fa-user-circle"></i><strong>' +
            d.user +
            '</strong><span class="comment-time">Just now</span></div><p class="comment-text">' +
            d.text +
            "</p>";
          var commentsList = document.getElementById("comments-list");
          if (commentsList) commentsList.prepend(div);
          var textarea = cf.querySelector("textarea");
          if (textarea) textarea.value = "";
        });
    });
  }

  // Rating
  var rw = document.getElementById("rate-widget");
  if (rw) {
    rw.querySelectorAll(".rate-star").forEach(function (s) {
      s.addEventListener("click", function () {
        var score = s.dataset.score;
        var csrfToken = document.querySelector("[name=csrfmiddlewaretoken]")
          ? document.querySelector("[name=csrfmiddlewaretoken]").value
          : "";
        fetch("/manga/rate/", {
          method: "POST",
          headers: {
            "X-CSRFToken": csrfToken,
            "Content-Type": "application/x-www-form-urlencoded",
          },
          body: "manga_id=" + rw.dataset.manga + "&score=" + score,
        })
          .then(function (r) {
            return r.json();
          })
          .then(function (d) {
            if (d.error) {
              alert(d.error);
              return;
            }
            var ratingVal = document.getElementById("rating-val");
            if (ratingVal) ratingVal.textContent = d.rating;
            rw.querySelectorAll(".rate-star").forEach(function (ss, i) {
              ss.querySelector("i").className =
                (i < score ? "fas" : "far") + " fa-star";
            });
          });
      });
    });
  }
});
