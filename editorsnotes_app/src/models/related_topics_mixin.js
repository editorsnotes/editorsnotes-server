"use strict";

module.exports = {
  constructor: function () {
    // This has to be inside here to prevent circular dependency (since
    // topics can have related topics)
    var RelatedTopicList = require('../collections/topic')

    this.relatedTopics = new RelatedTopicList([], { project: this.project }); 
  },
  mixin: {
    initialize: function () {
      this.listenTo(this.relatedTopics, 'add remove reset', this.refreshRelatedTopics);
      this.refreshRelatedTopics();
    },
    refreshRelatedTopics: function () {
      var topicURLs = this.relatedTopics.map(function (t) { return t.url() });
      this.set('related_topics', topicURLs);
    },
    parse: function (response) {
      if (response.related_topics) {
        this.relatedTopics.set(response.related_topics, { parse: true });
        delete response.related_topics;
      }

      return response;
    }
  }
}
