// Admin login page: checkbox to toggle next redirect
(function () {
  var cb = document.getElementById("to_default_admin");
  var nextInput = document.getElementById("id_next");
  var defaultNext = "/panel/";
  var adminIndex = "/admin/";

  // Read serverNext from data attribute on hidden div
  var serverNextDiv = document.querySelector("[data-server-next]");
  var serverNext = serverNextDiv
    ? serverNextDiv.getAttribute("data-server-next")
    : "";

  if (serverNext) {
    nextInput.value = serverNext;
  } else {
    nextInput.value = defaultNext;
  }

  if (cb) {
    cb.addEventListener("change", function () {
      if (cb.checked) {
        nextInput.value = adminIndex;
      } else {
        nextInput.value = defaultNext;
      }
    });
  }
})();
