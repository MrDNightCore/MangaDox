// Auto-dismiss messages after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
  setTimeout(function() {
    var msgs = document.getElementById('site-messages');
    if (msgs) {
      msgs.style.opacity = '0';
      msgs.style.transform = 'translateY(-20px)';
      setTimeout(function() {
        msgs.remove();
      }, 400);
    }
  }, 5000);
});
