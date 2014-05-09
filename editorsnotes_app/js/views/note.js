"use strict";

var Backbone = require('../backbone')
  , Cocktail = require('backbone.cocktail')
  , _ = require('underscore')
  , i18n = require('../utils/i18n').main
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
    'select[name="note-status"]': {
      observe: 'status',
      selectOptions: {
        collection: function () {
          return _.map(this.model.possibleStatuses, function (s) {
            return { value: s + '111', label: i18n.translate(s).fetch() }
          });
        }
      }
    },
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
    this.$('#note-description > :first-child').editText();
  }
});

Cocktail.mixin(NoteView, SaveItemMixin);
