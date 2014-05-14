"use strict";

var Backbone = require('../backbone')
  , Scan = require('../models/scan')

module.exports = Backbone.Collection.extend({
  model: Scan,
  initialize: function (models, options) {
    if (!options.document) {
      throw "Scan collection must be passed a document in its options."
    }
    this.dokument = options.document;
  },
  url: function () { return this.dokument.url() + 'scans/'; }
});
