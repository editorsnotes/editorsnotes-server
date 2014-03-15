"use strict";

var _ = require('underscore')
  , ProjectSpecificBaseModel = require('./project_specific_base')
  , NoteSectionList = require('../collections/note_section')
  , RelatedTopicList = require('../collections/topic')

module.exports = ProjectSpecificBaseModel.extend({
  defaults: {
    'title': null,
    'content': null,
    'status': 'open',
    'section_ordering': [],
    'related_topics': []
  },

  initialize: function () {
    var that = this;

    this.related_topics = new RelatedTopicList([], {
      project: this.project
    });

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
    var parsedNames = response.related_topics.map(function (t) { return t.name })
      , existingNames = this.related_topics.map(function (t) { return t.get('name') })
      , updateNames = !!_.difference(parsedNames, existingNames).length

    this.sections.set(response.sections);

    if (updateNames) {
      this.related_topics.set(response.related_topics);
      this.set('related_topics', parsedNames);
    }

    delete response.sections;
    delete response.related_topics;

    return response
  }
});
