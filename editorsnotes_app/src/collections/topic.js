"use strict";

var Backbone = require('../backbone')
  , Topic = require('../models/topic')

module.exports = Backbone.Collection.extend({
  model: Topic,

  initialize: function (models, options) {
    this.project = this.project || options.project
  },

  url: function () { return this.project.url() + 'topics/'; }
});
