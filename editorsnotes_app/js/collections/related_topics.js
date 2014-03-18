"use strict";

var Backbone = require('../backbone')
  , _ = require('underscore')
  , Topic = require('../models/topic')

module.exports = Backbone.Collection.extend({
  model: Topic,
  initialize: function (models, options) {
    this.project = options.project;
  },
  sync: function () { return null; },
  save: function () { return null; },
  fetch: function () {
    if (!this.url) return null;
    return Backbone.Collection.prototype.fetch.call(this, arguments);
  }
});
