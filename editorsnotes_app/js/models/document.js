"use strict";

var Backbone = require('../backbone')

module.exports = Backbone.Model.extend({
  initialize: function () {
    // As stated in project.js, for now, we only work with documents inside an instance
    // of DocumentCollection inside a Project. This stuff should be part of a
    // base model, but I didn't do that because method inheritence in javascript
    // is icky. (so, TODO)
    this.project = (this.collection && this.collection.project);
    if (!this.project) {
      throw new Error('Add notes through a project instance');
    }
  },

  url: function () {
    // Make sure URLs end with slashes. This should also be part of a base
    // model. (TODO)
    var origURL = Backbone.Model.prototype.url.call(this);
    return origURL.slice(-1) === '/' ? origURL : origURL + '/';
  },

  defaults: {
    description: null,
    zotero_data: null,
    topics: []
  }
});
