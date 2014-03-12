"use strict";

var Backbone = require('../backbone')

module.exports = Backbone.Model.extend({
  initialize: function () {
    this.project = this.collection && this.collection.project;
    if (!this.project) {
      throw new Error('Add notes through a project instance');
    }
  },

  defaults: {
    preferred_name: null,
    topic_node_id: null,
    type: null,
    summary: null
  },

  url: function () {
    return this.isNew() ?
      this.collection.url :
      this.colection.url + this.get('topic_node_id') + '/';
  }

});

