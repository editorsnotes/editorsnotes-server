"use strict";

var OrderedCollection = require('./ordered_collection')
  , NoteSection = require('../models/note_section')
  , ProjectSpecificMixin = require('../models/project_specific_mixin')

module.exports = OrderedCollection.extend({
  model: NoteSection,
  constructor: function () {
    ProjectSpecificMixin.constructor.apply(this, arguments);
    OrderedCollection.apply(this, arguments);
  },
  orderNormalizationURL: function () {
    return this.url + 'normalize_section_order/'
  },
  parse: function (response) { return response.sections }
});

