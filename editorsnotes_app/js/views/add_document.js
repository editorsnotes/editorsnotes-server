"use strict";

var AddItemView = require('./generic/add_item_base')
  , _ = require('underscore')

module.exports = AddItemView.extend({
  itemType: 'document',
  textarea: true,
  initialize: function () {
    var that = this
      , EditZoteroView = require('./edit_zotero');

    this.render();
    this.$('.modal-body').append('<div class="add-document-zotero-data">');
    this.zoteroView = new EditZoteroView({
      el: this.$('.add-document-zotero-data')
    });
    this.listenTo(this.zoteroView, 'updatedCitation', function (citation) {
      this.$('.item-text-main').val(citation);
      that.model.set('description', citation);
    });
    this.listenTo(this.zoteroView, 'updatedZoteroData', function (dataObj) {
      var data = _.isEmpty(dataObj) ? null : dataObj;
      that.model.set('zotero_data', data);
    });
  },

  render: function () {
    var that = this;
    this.renderModal();
    this.$el.on('hidden', function () {
      if (that.model.isNew()) that.model.destroy();
    });
  },

  saveItem: function (e) {
    var that = this;
    e.preventDefault();
    this.model.save().then(function () {
      that.$el.modal('hide')
    });
  }
});

