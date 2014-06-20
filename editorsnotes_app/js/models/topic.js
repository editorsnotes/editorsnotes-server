"use strict";

var Backbone = require('../backbone')
  , Cocktail = require('backbone.cocktail')
  , ProjectSpecificMixin = require('./project_specific_mixin')
  , RelatedTopicsMixin = require('./related_topics_mixin')
  , CitationList = require('../collections/citation')
  , Topic

module.exports = Topic = Backbone.Model.extend({
  defaults: {
    preferred_name: '',
    topic_node_id: null,
    type: null,
    related_topics: [],
    summary: ''
  },

  constructor: function () {
    var that = this;

    ProjectSpecificMixin.constructor.apply(this, arguments);
    RelatedTopicsMixin.constructor.apply(this, arguments);
    this.citations = new CitationList([]);
    this.citations.url = function () {
      return that.isNew() ? null : that.url() + 'citations/';
    };
    this.citations.project = this.project;
    Backbone.Model.apply(this, arguments);
  },

  urlRoot: function () {
    return this.project.url() + 'topics/';
  },

  url: function () {
    return this.isNew() ?
      this.urlRoot() :
      this.urlRoot() + this.get('topic_node_id') + '/';
  },

  parse: function (response) {
    this.citations.set(response.citations);
    delete response.sections;
    return response;
  }
});

Cocktail.mixin(Topic, RelatedTopicsMixin.mixin);
