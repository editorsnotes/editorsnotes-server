"use strict";

var Backbone = require('../backbone')

module.exports = Backbone.Model.extend({
  defaults: {
    'image_file': null,
    'ordering': null
  },
  sync: function(method, model, options) {
    var data;

    if (method === 'create' || method === 'update' || method === 'patch' || method === 'delete') {
      data = new FormData();
      if (method !== 'delete') {
        data.append('image', model.get('image_file'));
        // TODO: scan ordering!!!!!!!
        //data.append('ordering', model.get('ordering'));
      }
      options.cache = false;
      options.contentType = false;
      options.data = data;
      options.processData = false;
    }

    return Backbone.sync.call(this, method, model, options || {});
  },
  getFilename: function () {
    if (this.has('image')) {
      return this.get('image').replace(/.*\//, '');
    } else if (this.has('image_file')) {
      return this.get('image_file').fileName;
    } else {
      return null;
    }
  }
});
