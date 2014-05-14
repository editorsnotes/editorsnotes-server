"use strict";

var Backbone = require('../backbone')

module.exports = Backbone.Model.extend({
  defaults: {
    'image_file': null,
    'image_filename': null,
    'ordering': null
  },
  sync: function(method, model, options) {
    var data;

    if (method === 'create' || method === 'update' || method === 'patch' || method === 'delete') {
      data = new FormData();
      if (method !== 'delete') {
        data.append('image', this.get('image_file'), this.get('image_filename', null));
        data.append('ordering', this.get('ordering'));
      }
      options.cache = false;
      options.contentType = false;
      options.data = data;
      options.processData = false;
    }

    Backbone.sync.call(this, method, model, options || {});
  }
});
