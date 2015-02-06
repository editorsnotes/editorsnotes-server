"use strict";

var Backbone = require('../../../backbone')

module.exports = Backbone.View.extend({
  $modal: null,
  events: {
    'click': 'handleClick'
  },
  initialize: function () {
    this.render();
  },
  render: function () {
    var feedbackHtml = (
      '<div class="feedback-prompt">' +
        '<span class="feedback-label">Feedback</span>' +
        '<i class="fa fa-plus"></i>' +
      '</div>');

    this.$el.html(feedbackHtml);
  },
  handleClick: function (e) {
    var that = this
      , FeedbackModalView = require('./modal')
      , modalView = new FeedbackModalView({ purpose: 'Feedback' })

    e.preventDefault();

    modalView.$el.one('shown', function () { that.$el.hide() });
    modalView.$el.one('hidden', function () { that.$el.show() });
  }
});
