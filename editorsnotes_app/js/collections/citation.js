"use strict";

var Backbone = require('../backbone')
  , Citation = require('../models/citation')

module.exports = Backbone.Collection.extend({
  model: Citation
});
