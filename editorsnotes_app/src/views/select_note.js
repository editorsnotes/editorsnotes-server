"use strict";

var $ = require('../jquery')
  , SelectItemView = require('./generic/select_item_base')
  , Note = require('../models/note')

module.exports = SelectItemView.extend({
  type: 'note',
  labelAttr: 'title',
  autocompleteURL: function () { return this.project.url() + 'notes/'; },

  selectItem: function (event, ui) {
    this.trigger('noteSelected', new Note(ui.item));
  },

  addItem: function (e) {
    var that = this
      , AddNoteView = require('./generic/make_modal_view')('note')
      , addView = new AddNoteView({
        model: new Note({}, { project: this.project }),
        el: $('<div>').appendTo('body')
      });

    e.preventDefault();

    this.listenTo(addView.model, 'sync', function (item) {
      that.trigger('noteSelected', item);
    });
    addView.$el.modal();
  }
});

