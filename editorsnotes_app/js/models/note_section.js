"use strict";

var Backbone = require('../backbone')

module.exports = Backbone.Model.extend({
  idAttribute: 'section_id',

  initialize: function () {
    this.project = this.collection.project;
  },

  url: function () {
    return this.isNew() ?
      this.collection.url :
      this.collection.url + 's' + this.get('section_id') + '/';
  }
});

