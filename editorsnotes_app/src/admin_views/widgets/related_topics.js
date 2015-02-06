"use strict";

var Backbone = require('../../backbone')
  , $ = require('../../jquery')
  , Topic = require('../../models/topic')
  , Autocompleter = require('../../utils/autocomplete_widget')
  , RelatedTopicItemView

RelatedTopicItemView = Backbone.View.extend({
  events: {
    'click a.destroy': 'destroy'
  },
  className: 'related-topic',
  render: function () {
    this.$el.html('<a href="#" class="destroy"><i class="fa fa-minus-circle"></i></a>' + this.model.get('preferred_name'));
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
    'autocompleteselect': 'selectItem',
    'click .add-new-object': 'addItem'
  },
  className: 'related-topics-widget',
  initialize: function () {
    var autocompleter
      , template = require('../generic/templates/add_or_select_item.html')

    this.$topicList = $('<div class="related-topics-list">').appendTo(this.$el);

    this.listenTo(this.collection, 'add', this.addTopic);
    this.collection.forEach(this.addTopic, this);

    this.$search = $(template({ type: 'topic' }))
      .prependTo(this.$el)
      .filter('input')
        .css('width', '350px');

    autocompleter = new Autocompleter(this.$search, this.collection.project.get('slug'), 'topics');

  },
  addItem: function (e) {
    e.preventDefault();

    var AddTopicView = require('../generic/make_modal_view')('topic')
      , addView = new AddTopicView({
        model: new Topic({}, { project: this.collection.project }),
        el: $('<div>').appendTo('body')
      })

    this.listenTo(addView.model, 'sync', this.collection.add.bind(this.collection));

    addView.$el.modal();
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
    this.collection.add({
      url: ui.item.uri,
      preferred_name: ui.item.value
    });
  }
});
