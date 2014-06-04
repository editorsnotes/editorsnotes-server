"use strict";

var AddItemView = require('./generic/add_item_base')

module.exports = AddItemView.extend({
  itemType: 'note',
  initialize: function (options) {
    this.model = options.project.notes.add({}, {at: 0}).at(0);
    this.render();

    // TODO: assigned users & licensing
  },

  render: function () {
    var that = this;

    this.renderModal();

    this.$('.modal-body')
      .prepend('<h5>Title</h5>')
      .append(''
        + '<h5>Description</h5>'
        + '<textarea class="add-note-description" style="width: 98%; height: 80px;"></textarea>');
    this.$el.on('hidden', function () {
      if (that.model.isNew()) that.model.destroy();
    });
  },

  saveItem: function () {
    var that = this
      , data = {
        title: this.$('.item-text-main').val(),
        content: this.$('.add-note-description').val()
      }

    this.model.set(data);
    this.model.save(data, {
      success: function () { that.$el.modal('hide') }
    });
  }
});

