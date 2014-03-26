"use strict";

var _ = require('underscore')
  , ProjectSpecificBaseModel = require('./project_specific_base')
  , RelatedTopicsMixin = require('./related_topics_mixin')
  , Document

Document = ProjectSpecificBaseModel.extend({
  defaults: {
    description: null,
    zotero_data: null,
    related_topics: []
  },

  initialize: function () {
    this.refreshRelatedTopics();
  },
  
  urlRoot: function () {
    return this.project.url() + 'documents/';
  },

  parse: function (response) {
    this.getRelatedTopicList().set(response.related_topics || [], { parse: true });
    delete response.related_topics;
  }
});

_.extend(Document.prototype, RelatedTopicsMixin);
module.exports = Document;
