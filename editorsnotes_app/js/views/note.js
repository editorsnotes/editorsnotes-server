"use strict";

var Backbone = require('../backbone')
  , Cocktail = require('backbone.cocktail')
  , NoteSectionListView = require('./note_section_list')
  , RelatedTopicsView = require('./related_topics')
  , SaveItemMixin = require('./save_item_mixin')
  , NoteView

NoteView = module.exports = Backbone.View.extend({
  events: {
    'editor:input #note-description': function (e, data) {
      this.model.set('content', data);
    }
  },

  bindings: {
    'select[name="note-status"]': 'status',
    '#note-title': 'title'
  },

  initialize: function () {
    var note = this.model;

    this.sectionListView = new NoteSectionListView({ model: note });
    this.topicListView = new RelatedTopicsView({ collection: note.relatedTopics });

    this.render();
    this.stickit();
  },

  render: function () {
    var that = this
      , template = require('../templates/note.html')

    this.$el.empty().html(template({ note: that.model }));

    if (!this.model.isNew()) {
      this.sectionListView.setElement( that.$('#note-sections') );
      this.sectionListView.render()
    }

    this.topicListView.$el.appendTo( that.$('#note-authorship') );
    this.editDescription();
  },

  editDescription: function () {
    var $description = this.$('#note-description > :first-child').editText();
  }
});

Cocktail.mixin(NoteView, SaveItemMixin);
