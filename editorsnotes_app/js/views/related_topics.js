"use strict";

var Backbone = require('../backbone')
  , $ = require('../jquery')
  , Autocompleter = require('../utils/autocomplete_widget')
  , RelatedTopicItemView

RelatedTopicItemView = Backbone.View.extend({
  events: {
    'click a.destroy': 'destroy'
  },
  className: 'related-topic',
  render: function () {
    this.$el.html('<a href="#" class="destroy"><i class="icon-minus-sign"></i></a>' + this.model.get('preferred_name'));
  },
  destroy: function (e) { 
    var that = this;
    e.preventDefault();
    this.model.collection.remove(this.model);
    this.$el.fadeOut(function () {
      that.remove()
    });
  }
});

module.exports = Backbone.View.extend({
  events: {
    'autocompleteselect': 'selectItem'
  },
  className: 'related-topics-widget',
  initialize: function (options) {
    var autocompleter;
    this.$topicList = $('<div class="related-topics-list">').appendTo(this.$el);

    this.listenTo(this.collection, 'add', this.addTopic);
    this.collection.forEach(this.addTopic, this);

    this.$search = $('<input type="text">').prependTo(this.$el);
    autocompleter = new Autocompleter(this.$search, this.collection.project.get('slug'), 'topics');

  },
  addTopic: function (topic) {
    var view = new RelatedTopicItemView({ model: topic });
    view.render();
    this.$topicList.append( view.$el );
  },
  addAllTopics: function (collection) {
    collection.forEach(this.addTopic, this);
  },
  selectItem: function (event, ui) {
    if (!ui.item) return;
    event.preventDefault();
    event.target.value = '';
    var topic = this.collection.add({
      url: ui.item.uri,
      preferred_name: ui.item.value
    });
  }
});
