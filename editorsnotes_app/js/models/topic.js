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

  idAttribute: 'slugnode',

  initialize: function () {
    this.refreshRelatedTopics();
  },

  parse: function (response) {
    if (!response.topic_node_id) {
      if (response.id) {
        response.topic_node_id = response.id;
      } else if (response.url) {
        response.topic_node_id = response.url.match(/\/topics\/([^\/]+)\//)[1];
      }
    }
    response.slugnode = this.project.get('slug') + response.topic_node_id;
    if (response.name && !response.preferred_name) {
      response.preferred_name = response.name;
    }

    this.getRelatedTopicList().set(response.related_topics || [], { parse: true });

    delete response.related_topics;
    delete response.name;
    delete response.id;

    return response
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
