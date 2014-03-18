"use strict";

var ProjectSpecificBaseModel = require('./project_specific_base')

module.exports = ProjectSpecificBaseModel.extend({
  defaults: {
    preferred_name: null,
    topic_node_id: null,
    type: null,
    summary: null
  },

  idAttribute: 'slugnode',

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

