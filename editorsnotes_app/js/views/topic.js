"use strict";

var _ = require('underscore')
  , $ = require('../jquery')
  , Backbone = require('../backbone')
  , Cocktail = require('backbone.cocktail')
  , RelatedTopicsView = require('./related_topics')
  , CitationsView = require('./citations')
  , SaveItemMixin = require('./save_item_mixin')
  , TopicView

module.exports = TopicView = Backbone.View.extend({
  events: {
    'editor:input #topic-summary': function (e, data) {
      this.model.set('summary', data);
    }
  },
  bindings: {
    '#topic-type': 'type',
    '#topic-name': 'preferred_name'
  },
  initialize: function (options) {
    var that = this;
    this.topicListView = new RelatedTopicsView({ collection: that.model.relatedTopics });
    this.render();
    this.citationListView = new CitationsView({
      el: '#topic-citations',
      collection: that.model.citations
    });
    this.stickit();
  },

  render: function () {
    var that = this
      , template = require('../templates/topic.html')

    this.$el.html( template({ topic: that.model, _: _ }));
    this.$('#topic-summary > :first-child').editText();

    $.getJSON('/api/metadata/topics/types/', function (data) {
      var options = _.chain(data.types).map(function (d) {
        var option = document.createElement('option');
        option.value = d.key;
        option.innerHTML = d.localized;
        return option;
      }).flatten().sort().value();
      $('#topic-type').append(options);
    });

    this.topicListView.$el.appendTo( that.$('#topic-related-topics') );
  }

});

Cocktail.mixin(TopicView, SaveItemMixin);
