EditorsNotes.Views = {}
EditorsNotes.Models = {}
EditorsNotes.Templates = {}

EditorsNotes.wysihtml5BaseOpts = {
  parserRules: wysihtml5ParserRules,
  stylesheets: ['/static/function/wysihtml5/stylesheet.css'],
  useLineBreaks: false
}

// Change backbone sync so that we include the CSRF token before each request.
//
// TODO: only include it with write operations
var oldSync = Backbone.sync;
Backbone.sync = function (method, model, options) {
  options.beforeSend = function (xhr) {
    var token = $('input[name="csrfmiddlewaretoken"]').val()

    if (!token) {
      console.error('No CSRF token found.');
      return;
    }

    xhr.setRequestHeader('X-CSRFToken', token);
  }
  return oldSync(method, model, options);
};

