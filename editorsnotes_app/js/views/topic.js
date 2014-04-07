"use strict";

var _ = require('underscore')
  , Backbone = require('../backbone')
  , RelatedTopicsView = require('./related_topics')

module.exports = Backbone.View.extend({
  initialize: function (options) {
    var that = this;
    this.topicListView = new RelatedTopicsView({ collection: that.model.relatedTopics });
  },

  render: function () {
    var that = this
      , template = require('../templates/topic.html')

    this.$el.html(template({ topic: that.model, _: _ }));
    this.$('#topic-summary').editText();

    this.topicListView.$el.appendTo( that.$('#topic-related-topics') );
  }

});
