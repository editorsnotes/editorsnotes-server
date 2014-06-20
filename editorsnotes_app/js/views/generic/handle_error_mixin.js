"use strict";

var _ = require('underscore')
  , $ = require('../../jquery')

function animateErrorEl(html, container) {
  return $(html).hide().prependTo(container).fadeIn();
}

module.exports = {
  initialize: function () {
    if (this.model) {
      this.listenTo(this.model, 'error', this._handleError);
      this.listenTo(this.model, 'request', this._emptyErrors);
    }
    if (this.collection) {
      this.listenTo(this.collection, 'error', this._handleError);
      this.listenTo(this.collection, 'request', this._emptyErrors);
    }
  },
  _handleError: function (modelOrCollection, resp) {
    var template = require('../../templates/error_message.html')
      , miscErrors = {}

    _.forEach(resp.responseJSON, function (errors, key) {
      var $container = this.$('[data-error-target="' + key + '"]')
        , errorObj

      if (!$container.length) {
        miscErrors[key] = errors;
        return;
      }

      errorObj = {};
      errorObj[key] = errors;
      animateErrorEl(template({ errors: errorObj, includeLabel: false }), $container);
    }, this);

    if (!_.isEmpty(miscErrors)) {
      animateErrorEl(template({ errors: miscErrors, includeLabel: true }), this.$el);
    }
  },
  _emptyErrors: function () {
    this.$('.error-message').remove();
  }
}
