"use strict";

var Backbone = require('../backbone')
  , Cocktail = require('backbone.cocktail')
  , ProjectSpecificMixin = require('./project_specific_mixin')
  , RelatedTopicsMixin = require('./related_topics_mixin')
  , NoteSectionList = require('../collections/note_section')
  , Note

module.exports = Note = Backbone.Model.extend({
  defaults: {
    'title': null,
    'content': null,
    'status': 'open',
    'section_ordering': [],
    'related_topics': []
  },

  constructor: function () {
    ProjectSpecificMixin.constructor.apply(this, arguments);
    RelatedTopicsMixin.constructor.apply(this, arguments);
    this.sections = new NoteSectionList([], {
      project: this.project
    });
    Backbone.Model.apply(this, arguments);
  },

  initialize: function () {
    var that = this;
    this.sections.url = this.url();
    this.sections.comparator = function (section) {
      return that.get('section_order').indexOf(section.id);
    }
  },

  urlRoot: function () {
    return this.project.url() + 'notes/';
  },

  possibleStatuses: ['open', 'closed', 'hibernating'],

  parse: function (response) {
    this.sections.set(response.sections);
    delete response.sections;

    return response;
  }
});

Cocktail.mixin(Note, RelatedTopicsMixin.mixin)
