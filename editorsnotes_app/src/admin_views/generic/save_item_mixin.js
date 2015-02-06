"use strict";

var _ = require('underscore')
  , $ = require('../../jquery')

module.exports = {
  events: {
    'click .save-item': '_handleSave',
    'click .delete-item': '_handleDelete'
    
  },
  render: function () {
    var template = require('./templates/save_row.html');
    this.$el.append(template({ model: this.model }));
  },
  toggleLoaders: function (state) {
    this.$('.save-item').prop('disabled', state);
    this.$('.loader').toggle(state);
  },
  _handleSave: function () {
    if (this.saveItem) {
      this.saveItem();
    } else {
      this.defaultSave();
    }
  },
  defaultSave: function () {
    var that = this;

    this.toggleLoaders(true);
    this.model.save()
      .always(this.toggleLoaders.bind(this, false))
      .done(function () {
        window.location.href = that.model.url().replace('\/api\/', '/');
      })
  },
  _handleDelete: function () {
    if (this.deleteItem) {
      this.deleteItem();
    } else {
      this.defaultDelete();
    }
  },
  defaultDelete: function () {
    var that = this
      , template = require('./templates/confirm_delete.html')
      , promise = $.get(this.model.url() + 'confirm_delete/')

    promise.done(function (data) {
      var modal = template({ _ : _, items: data.items })
        , $modal = $(modal).appendTo('body').modal()

      $modal
        .on('hidden', $modal.remove)
        .find('.btn-delete-item').on('click', function () {
          that.model.destroy()
            .done(function () {
              window.location.href = that.model.project.url().replace('\/api\/', '/');
            });
        });
    });
  }
}
