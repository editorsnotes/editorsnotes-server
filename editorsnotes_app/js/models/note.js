"use strict";

var Backbone = require('../backbone')
  , NoteSectionList = require('../collections/note_section')

module.exports = Backbone.Model.extend({
  url: function() {
    // Same as EditorsNotes.Models.Document.url (ergo, same TODO as there)
    var origURL = Backbone.Model.prototype.url.call(this);
    return origURL.slice(-1) === '/' ? origURL : origURL + '/';
  },

  defaults: {
    'title': null,
    'content': null,
    'status': '1',
    'section_ordering': [],
    'related_topics': []
  },

  initialize: function (options) {
    var that = this;

    // Same as in EditorsNotes.Models.Document.initialize (TODO)
    this.project = (this.collection && this.collection.project);
    if (!this.project) {
      throw new Error('Add notes through a project instance');
    }

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
    this.related_topics = [];
  },

  parse: function (response) {
    var topicNames = response.related_topics.map(function (t) { return t.name });

    this.sections.set(response.sections);
    this.set('related_topics', topicNames);

    delete response.sections;
    delete response.related_topics;

    return response
  }
});
