"use strict";

var Backbone = require('../backbone')
  , Note = require('../models/note')

module.exports = Backbone.Collection.extend({
  model: Note,

  url: function () { return this.project.url() + 'notes/'; },

  initialize: function (models, options) {
    this.project = options.project;
  }
});

