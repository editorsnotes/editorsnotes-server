"use strict";

var _ = require('underscore')
  , ProjectSpecificBaseModel = require('./project_specific_base')
  , RelatedTopicsMixin = require('./related_topics_mixin')
  , NoteSectionList = require('../collections/note_section')
  , Note

Note = ProjectSpecificBaseModel.extend({
  defaults: {
    'title': null,
    'content': null,
    'status': 'open',
    'section_ordering': [],
    'related_topics': []
  },

  initialize: function () {
    var that = this;

    this.refreshRelatedTopics();

    // Add a collection of NoteSection items to this note
    this.sections = new NoteSectionList([], {
      url: that.url(),
      project: this.project
    });

    // Section ordering is a property of the Note, not the the individual
    // sections. So make them aware of that.
    this.sections.comparator = function (section) {
      var ordering = that.get('section_ordering');
      return ordering.indexOf(section.id);
    }
  },

  urlRoot: function () {
    return this.project.url() + 'notes/';
  },

  possibleStatuses: ['open', 'closed', 'hibernating'],

  parse: function (response) {
    this.sections.set(response.sections);
    this.getRelatedTopicList().set(response.related_topics || [], { parse: true });

    delete response.sections;
    delete response.related_topics;

    return response
  }
});

_.extend(Note.prototype, RelatedTopicsMixin);

module.exports = Note;
