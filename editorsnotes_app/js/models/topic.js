"use strict";

var Backbone = require('../backbone')
  , Cocktail = require('backbone.cocktail')
  , ProjectSpecificMixin = require('./project_specific_mixin')
  , RelatedTopicsMixin = require('./related_topics_mixin')
  , Topic

module.exports = Topic = Backbone.Model.extend({
  defaults: {
    preferred_name: null,
    topic_node_id: null,
    type: null,
    related_topics: [],
    summary: null
  },

  constructor: function () {
    ProjectSpecificMixin.constructor.apply(this, arguments);
    RelatedTopicsMixin.constructor.apply(this, arguments);
    Backbone.Model.apply(this, arguments);
  },

  urlRoot: function () {
    return this.project.url() + 'topics/';
  },

  url: function () {
    return this.isNew() ?
      this.urlRoot() :
      this.urlRoot() + this.get('topic_node_id') + '/';
  }
});

Cocktail.mixin(Topic, RelatedTopicsMixin.mixin);
