;

(function () {
  var failStr = 'bid_login_failed=1'
    , loginFailed = location.search.indexOf(failStr) !== -1
    , logoutURL = loginFailed ? '/accounts/login/?bad_email=1' : null
  ;

  $(document).on('click', '.browserid-login', function (e) {
    e.preventDefault();
    $loginButton = $(this);
    navigator.id.request({
      'siteName': "Editorsʼ Notes" // apostrophe is blocked, this is u02bc
    });
  });

  $(document).on('click', '.browserid-logout', function (e) {
    e.preventDefault();
    logoutURL = this.href;
    navigator.id.logout();
  });

  navigator.id.watch({
    loggedInUser: EditorsNotes.loggedInUser,

    onlogin: function (assertion) {
      if (loginFailed) {
        navigator.id.logout();
        return;
      }
      if (assertion) {
        var $assertion = $('#id_assertion');
        $assertion.val(assertion.toString());
        $assertion.parent('form').submit();
      }
    },

    onlogout: function () {
      if (logoutURL !== null) {
        window.location = logoutURL;
      }
    }

  });

})();
