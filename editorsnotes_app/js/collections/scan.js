"use strict";

var OrderedCollection = require('./ordered_collection')
  , Scan = require('../models/scan')

module.exports = OrderedCollection.extend({
  model: Scan,
  initialize: function (models, options) {
    if (!options.document) {
      throw "Scan collection must be passed a document in its options."
    }
    this.dokument = options.document;

    OrderedCollection.prototype.initialize.apply(this, arguments);
  },
  url: function () { return this.dokument.url() + 'scans/'; }
});
