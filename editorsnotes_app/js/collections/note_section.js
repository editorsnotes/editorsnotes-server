"use strict";

var Backbone = require('../backbone')
  , NoteSection = require('../models/note_section')

module.exports = Backbone.Collection.extend({
  model: NoteSection,

  initialize: function (models, options) {
    this.project = options.project;
  },

  parse: function (response) { return response.sections; }
});

