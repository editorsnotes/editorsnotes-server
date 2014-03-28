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
      this.listenTo(this.relatedTopics, 'add', this.refreshRelatedTopics);
      this.listenTo(this.relatedTopics, 'remove', this.refreshRelatedTopics);
      this.listenTo(this.relatedTopics, 'reset', this.refreshRelatedTopics);
      this.refreshRelatedTopics();
    },
    refreshRelatedTopics: function (e) {
      var topicNames = this.relatedTopics.map(function (t) {
        return t.get('preferred_name')
      });
      this.set('related_topics', topicNames);
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
