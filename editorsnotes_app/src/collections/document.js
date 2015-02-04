"use strict";

var Backbone = require('../backbone')
  , Document = require('../models/document')

module.exports = Backbone.Collection.extend({
  model: Document,

  initialize: function (models, options) {
    this.project = this.project || options.project;
  },

  url: function () { return this.project.url() + 'documents/'; }
});

