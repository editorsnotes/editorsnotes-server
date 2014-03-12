"use strict";

var Backbone = require('backbone')
  , oldSync = Backbone.sync
  , $ = require('jquery')

Backbone.$ = $

Backbone.sync = function (method, model, options) {
  
  // Set a header with the CSRF token before sending any requests
  options.beforeSend = function (xhr) {
    var token = $('input[name="csrfmiddlewaretoken"]').val();

    if (!token) {
      console.error('No CSRF token found.');
      return;
    }

    xhr.setRequestHeader('X-CSRFToken', token);
  }

  return oldSync(method, model, options);
}

module.exports = Backbone;
