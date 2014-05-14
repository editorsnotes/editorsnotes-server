"use strict";

var Backbone = require('../backbone')

module.exports = Backbone.View.extend({
  initialize: function () {
    this.render();
  },
  render: function () {
    var that = this
      , template = require('../templates/scans.html')

    this.$el.html( template({ scans: that.collection }) );
  }
});
