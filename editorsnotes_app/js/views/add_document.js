"use strict";

var AddItemView = require('./add_item')
  , _ = require('underscore')
  , Document = require('../models/document')

module.exports = AddItemView.extend({
  itemType: 'document',
  textarea: true,
  initialize: function (options) {
    var EditZoteroView = require('./edit_zotero');

    this.model = new Document({}, { project: options.project });
    this.render();
    this.$('.modal-body').append('<div class="add-document-zotero-data">');
    this.zoteroView = new EditZoteroView({
      el: this.$('.add-document-zotero-data')
    });
    this.listenTo(this.zoteroView, 'updatedCitation', function (citation) {
      this.$('.item-text-main').val(citation);
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
    var that = this
      , data = { description: this.$('.item-text-main').val() }
      , zotero_data = this.zoteroView.getZoteroData();

    e.preventDefault();

    if (!_.isEmpty(zotero_data)) {
      data.zotero_data = JSON.stringify(zotero_data);
    }

    this.model.set(data);
    this.model.save(data, {
      success: function () { that.$el.modal('hide') }
    });

  }
});

