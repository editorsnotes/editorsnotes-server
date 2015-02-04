"use strict";

var Backbone = require('../backbone')

module.exports = Backbone.Model.extend({
  defaults: {
    'document': null,
    'notes': null,
    'ordering': null
  }
});
