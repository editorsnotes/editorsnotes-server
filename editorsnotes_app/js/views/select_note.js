"use strict";

var SelectItemView = require('./select_item')

module.exports = SelectItemView.extend({
  type: 'note',
  labelAttr: 'title',
  autocompleteURL: function () { return this.project.url() + 'notes/'; },

  selectItem: function (event, ui) {
    this.trigger('noteSelected', this.project.notes.add(ui.item).get(ui.item.id));
  },

  addItem: function (e) {
    var that = this
      , AddNoteView = require('./add_note')
      , addView = new AddNoteView({ project: this.project });

    e.preventDefault();

    this.listenTo(addView.model, 'sync', function (item) {
      that.trigger('noteSelected', item);
    });
    addView.$el.appendTo('body').modal();
  }
});

