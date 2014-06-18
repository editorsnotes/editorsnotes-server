"use strict";

var _ = require('underscore')
  , Backbone = require('../backbone')
  , FEEDBACK_URL = '/accounts/profile/feedback/'

var FEEDBACK_URL

module.exports = Backbone.View.extend({
  events: {
    'hidden': 'remove',
    'click [data-action="submit"]': 'submit'
  },
  className: 'modal feedback-modal',
  initialize: function (options) {
    this.purpose = options && options.purpose;
    this.render();
  },
  render: function () {
    var that = this
      , template = require('../templates/feedback_modal.html');

    $.get(FEEDBACK_URL).done(function (form) {
      that.$el
        .appendTo('body')
        .html(template({ title: 'Submit feedback', form: form }))
        .modal();

      if (that.purpose && !that.$('option:selected').val()) {
        _.chain(that.$('option'))
          .filter(function (el) { return el.textContent.match(that.purpose) })
          .forEach(function (el) { el.selected = 'selected' });
      }
    });
  },
  submit: function () {
    var that = this
      , $modalBody = this.$('.modal-body')
      , $btns = this.$('button').prop('disabled', 'disabled')

    $.post(FEEDBACK_URL, this.$('form').serialize(), function (form) {
      $btns.prop('disabled', false);
      $modalBody.html(form);
    });
  }
});
