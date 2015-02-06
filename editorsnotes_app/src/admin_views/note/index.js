"use strict";

var Backbone = require('../../backbone')
  , Cocktail = require('backbone.cocktail')
  , _ = require('underscore')
  , i18n = require('../../utils/i18n').main
  , NoteSectionListView = require('./note_section_list')
  , RelatedTopicsView = require('../widgets/related_topics')
  , SaveItemMixin = require('../generic/save_item_mixin')
  , HandleErrorMixin = require('../generic/handle_error_mixin')
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
            return { value: s, label: i18n.translate(s).fetch() }
          });
        }
      }
    },
    '#note-private': {
      observe: 'is_private',
      selectOptions: {
        collection: function () {
          return [{ label: 'Yes', value: true }, { label: 'No', value: false }]
        }
      }
    },
    '#note-title': 'title'
  },

  initialize: function () {
    var note = this.model;
    this.sectionListView = new NoteSectionListView({ collection: note.sections });
    this.topicListView = new RelatedTopicsView({ collection: note.relatedTopics });
    this.render();
    this.stickit();
  },

  render: function () {
    var that = this
      , template = require('./templates/note.html')

    this.$el.empty().html(template({ note: that.model }));

    this.sectionListView.setElement( that.$('#note-sections') );
    this.sectionListView.render()

    this.topicListView.$el.appendTo( that.$('#note-related-topics') );
    this.$('#note-description > :first-child').editText();
  }
});

Cocktail.mixin(NoteView, SaveItemMixin, HandleErrorMixin);
