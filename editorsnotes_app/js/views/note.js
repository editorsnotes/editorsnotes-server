"use strict";

var Backbone = require('../backbone')
  , NoteSectionListView = require('./note_section_list')
  , RelatedTopicsView = require('./related_topics')

module.exports = Backbone.View.extend({
  events: {
    'click .save-item': 'saveItem',
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
      , saveRow = require('../templates/save_row.html')()

    this.$el.empty().html(template({ note: that.model }) + saveRow);

    if (!this.model.isNew()) {
      this.sectionListView.setElement( that.$('#note-sections') );
      this.sectionListView.render()
    }

    this.topicListView.$el.appendTo( that.$('#note-authorship') );
    this.editDescription();
  },

  editDescription: function () {
    var $description = this.$('#note-description > :first-child').editText();
  },

  toggleLoaders: function (state) {
    this.$('.save-item').prop('disabled', state);
    this.$('.loader').toggle(state);
  },

  saveItem: function () {
    var that = this;

    this.toggleLoaders(true);
    this.model.save()
      .always(this.toggleLoaders.bind(this, false))
      .done(function () {
        window.location.href = that.model.url().replace('\/api\/', '/');
      });
  }
});
