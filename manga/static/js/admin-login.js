// Admin login page: checkbox to toggle next redirect
(function () {
  var cb = document.getElementById("to_default_admin");
  var nextInput = document.getElementById("id_next");
  var defaultNext = "/panel/";
  var adminIndex = "/admin/";

  // if the server provided a next param that isn't the admin index, keep it
  var serverNext = document.body.getAttribute("data-server-next") || "";

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
