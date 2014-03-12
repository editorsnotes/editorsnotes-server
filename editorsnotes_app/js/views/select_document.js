"use strict";

var SelectItemView = require('./select_item')

module.exports =  SelectItemView.extend({
  type: 'document',
  labelAttr: 'description',
  autocompleteURL: function () { return this.project.url() + 'documents/' },

  selectItem: function (event, ui) {
    this.trigger('documentSelected', this.project.documents.add(ui.item).get(ui.item.id));
  },

  addItem: function (e) {
    var that = this
      , AddDocumentView = require('./add_document')
      , addView = new AddDocumentView({ project: this.project });

    e.preventDefault();

    this.listenTo(addView.model, 'sync', function (item) {
      that.trigger('documentSelected', item);
    });
    addView.$el.appendTo('body').modal();
  }
});

