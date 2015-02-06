"use strict";

var Backbone = require('../backbone')
  , Cocktail = require('backbone.cocktail')
  , ProjectSpecificMixin = require('./project_specific_mixin')
  , RelatedTopicsMixin = require('./related_topics_mixin')
  , ScanList = require('../collections/scan')
  , Document

module.exports = Document = Backbone.Model.extend({
  defaults: {
    description: null,
    zotero_data: null,
    related_topics: []
  },

  constructor: function () {
    ProjectSpecificMixin.constructor.apply(this, arguments);
    RelatedTopicsMixin.constructor.apply(this, arguments);
    this.scans = new ScanList([], { "document": this });
    Backbone.Model.apply(this, arguments);
  },

  urlRoot: function () {
    return this.project.url() + 'documents/';
  },

  parse: function (response) {
    this.scans.set(response.scans);
    delete response.scans;
    return response;
  }
});

Cocktail.mixin(Document, RelatedTopicsMixin.mixin);
