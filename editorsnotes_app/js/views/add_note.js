"use strict";

var Cocktail = require('backbone.cocktail')
  , NoteView = require('./note')
  , AddItemMixin = require('./generic/add_item_base')

module.exports = Cocktail.mixin(NoteView.extend({}), AddItemMixin, {
  itemType: 'note',
  initialize: function () {
    this.$('.save-row').remove();
    this.renderModal();
  },
  saveItem: function (e) {
    e.preventDefault();
    this.model.save().then(this.$el.modal.bind(this.$el, 'hide'));
  }
});

