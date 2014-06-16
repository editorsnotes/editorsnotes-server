"use strict";

var Cocktail = require('backbone.cocktail')
  , TopicView = require('./topic')
  , AddItemMixin = require('./generic/add_item_base')

module.exports = Cocktail.mixin(TopicView, AddItemMixin, {
  itemType: 'topic',
  initialize: function () {
    this.$('.save-row').remove();
    this.renderModal();
  },
  saveItem: function (e) {
    e.preventDefault();
    this.model.save().then(this.$el.modal.bind(this.$el, 'hide'));
  }
});
