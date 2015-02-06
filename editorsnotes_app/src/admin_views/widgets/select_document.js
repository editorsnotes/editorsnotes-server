"use strict";

var SelectItemView = require('../generic/select_item_base')
  , Document = require('../../models/document')

module.exports =  SelectItemView.extend({
  type: 'document',
  labelAttr: 'description',
  autocompleteURL: function () { return this.project.url() + 'documents/' },

  selectItem: function (event, ui) {
    this.trigger('documentSelected', new Document(ui.item));
  },

  addItem: function (e) {
    var that = this
      , AddDocumentView = require('../generic/make_modal_view')('document')
      , addView = new AddDocumentView({ model: new Document({}, { project: this.project }) });

    e.preventDefault();

    this.listenTo(addView.model, 'sync', function (item) {
      that.trigger('documentSelected', item);
    });
    addView.$el.appendTo('body').modal();
  }
});

