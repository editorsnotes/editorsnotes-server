"use strict";

var OrderedCollection = require('./ordered_collection')
  , Citation = require('../models/citation')

module.exports = OrderedCollection.extend({
  model: Citation
});
