"use strict";

var Backbone = require('../backbone')
  , Cocktail = require('backbone.cocktail')
  , ProjectSpecificMixin = require('./project_specific_mixin')
  , RelatedTopicsMixin = require('./related_topics_mixin')
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
    Backbone.Model.apply(this, arguments);
  },

  urlRoot: function () {
    return this.project.url() + 'documents/';
  }
});

Cocktail.mixin(Document, RelatedTopicsMixin.mixin);
