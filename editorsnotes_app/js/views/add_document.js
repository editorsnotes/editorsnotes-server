"use strict";

var Cocktail = require('backbone.cocktail')
  , DocumentView = require('./document')
  , AddItemMixin = require('./generic/add_item_base')

module.exports = Cocktail.mixin(DocumentView.extend({}), AddItemMixin, {
  itemType: 'document',
  initialize: function () {
    this.$('.save-row').remove();
    this.renderModal();
    this.generateCitation();
  },
  saveItem: function (e) {
    var that = this;
    e.preventDefault();
    this.model.save().then(function () {
      that.$el.modal('hide')
    });
  }
});
