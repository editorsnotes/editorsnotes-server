"use strict";

var saveRow = require('../templates/save_row.html')();

module.exports = {
  events: {
    'click .save-item': '_handleSave'
  },
  render: function () {
    this.$el.append(saveRow)
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
      });
  }
}
