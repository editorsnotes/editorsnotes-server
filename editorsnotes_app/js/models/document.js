"use strict";

var ProjectSpecificBaseModel = require('./project_specific_base')

module.exports = ProjectSpecificBaseModel.extend({
  defaults: {
    description: null,
    zotero_data: null,
    topics: []
  },
  
  urlRoot: function () {
    return this.project.url() + 'documents/';
  }
});
