"use strict";

var Backbone = require('../backbone')
  , RelatedTopicsView = require('./related_topics')
  , ZoteroDataView = require('./edit_zotero')

module.exports = Backbone.View.extend({
  events: {
    'click .save-item': 'saveItem'
  },

  initialize: function (options) {
    var that = this;

    this.topicListView = new RelatedTopicsView({ collection: that.model.relatedTopics });

    this.zoteroView = new ZoteroDataView({ zoteroData: that.model.get('zotero_data') });
    this.listenTo(this.zoteroView, 'updatedCitation', function (data) {
      that.$('#document-citation').html(data);
      that.model.set('description', data);
    });
    this.listenTo(this.zoteroView, 'updatedZoteroData', function (data) {
      that.model.set('zotero_data', data);
    });

  },

  render: function () {
    var that = this
      , template = require('../templates/document.html')
      , saveRow = require('../templates/save_row.html')()

    this.$el.html( template({ doc: that.model }) + saveRow );

    this.topicListView.$el.appendTo( that.$('#document-related-topics') );
    this.zoteroView.$el.appendTo( that.$('#document-zotero-data') );
  },

  toggleLoaders: function (state) {
    this.$('.save-item').prop('disabled', state);
    this.$('.loader').toggle(state);
  },

  saveItem: function () {
    var that = this;

    this.toggleLoaders(true);
    this.model.save()
      .always(this.toggleLoaders.bind(this, false))
      .done(function () {
        window.location.href = that.model.url().replace('\/api\/', '/');
      });
  }

});
