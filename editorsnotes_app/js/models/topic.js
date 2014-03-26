"use strict";

var _ = require('underscore')
  , ProjectSpecificBaseModel = require('./project_specific_base')
  , RelatedTopicsMixin = require('./related_topics_mixin')
  , Topic

Topic = ProjectSpecificBaseModel.extend({
  defaults: {
    preferred_name: null,
    topic_node_id: null,
    type: null,
    related_topics: [],
    summary: null
  },

  initialize: function () {
    this.refreshRelatedTopics();
  },

  parse: function (response) {
    this.getRelatedTopicList().set(response.related_topics || [], { parse: true });
    delete response.related_topics;

    return response;
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

_.extend(Topic.prototype, RelatedTopicsMixin);
module.exports = Topic;
