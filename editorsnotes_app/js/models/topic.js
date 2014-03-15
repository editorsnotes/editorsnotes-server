"use strict";

var ProjectSpecificBaseModel = require('./project_specific_base')

module.exports = ProjectSpecificBaseModel.extend({
  defaults: {
    preferred_name: null,
    topic_node_id: null,
    type: null,
    summary: null
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

