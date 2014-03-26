"use strict";

module.exports = {
  getRelatedTopicList: function () {
    // This has to be inside here to prevent circular dependency (since
    // topics can have related topics)
    var RelatedTopicList = require('../collections/topic')
    if (!this.hasOwnProperty('relatedTopics')) {
      this.relatedTopics = new RelatedTopicList([], { project: this.project }); 
      this.listenTo(this.relatedTopics, 'add', this.refreshRelatedTopics);
      this.listenTo(this.relatedTopics, 'remove', this.refreshRelatedTopics);
    }
    return this.relatedTopics;
  },
  refreshRelatedTopics: function () {
    var topicNames = this.getRelatedTopicList().map(function (t) {
      return t.get('preferred_name')
    });
    this.set('related_topics', topicNames);
  }
}
