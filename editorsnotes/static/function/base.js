jQuery.fn.log = function (message) {
  return this.each(function() {
    if (window.console) {
      console.log('%s: %o', message, this);
    }
  });
};
$(document).ready(function () {
  // Initialize timeago.
  $('time.timeago').timeago();
});
