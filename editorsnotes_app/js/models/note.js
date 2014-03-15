"use strict";

var Backbone = require('../backbone')
  , _ = require('underscore')
  , NoteSectionList = require('../collections/note_section')
  , RelatedTopicList = require('../collections/topic')

module.exports = Backbone.Model.extend({
  urlRoot: function () {
    return this.project.url() + 'notes/';
  },

  url: function() {
    // Same as EditorsNotes.Models.Document.url (ergo, same TODO as there)
    var origURL = Backbone.Model.prototype.url.call(this);
    return origURL.slice(-1) === '/' ? origURL : origURL + '/';
  },

  defaults: {
    'title': null,
    'content': null,
    'status': 'open',
    'section_ordering': [],
    'related_topics': []
  },

  initialize: function (attributes, options) {
    var that = this;

    // Same as in EditorsNotes.Models.Document.initialize (TODO)
    this.project = (options && options.project) || (this.collection && this.collection.project);
    if (!this.project) {
      throw new Error('Notes must have a project set, either explicitly or through a collection.')
    }

    // Add a collection of NoteSection items to this note
    this.sections = new NoteSectionList([], {
      url: that.url(),
      project: this.project
    });

    this.related_topics = new RelatedTopicList([], {
      project: this.project
    });

    // Section ordering is a property of the Note, not the the individual
    // sections. So make them aware of that.
    this.sections.comparator = function (section) {
      var ordering = that.get('section_ordering');
      return ordering.indexOf(section.id);
    }
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
