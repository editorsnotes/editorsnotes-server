"use strict";

var Backbone = require('../backbone')
  , NoteSection = require('../models/note_section')
  , ProjectSpecificMixin = require('../models/project_specific_mixin')

module.exports = Backbone.Collection.extend({
  model: NoteSection,
  constructor: function () {
    ProjectSpecificMixin.constructor.apply(this, arguments);
    Backbone.Collection.apply(this, arguments);
  }
});

