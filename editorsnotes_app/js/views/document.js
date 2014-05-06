"use strict";

var Backbone = require('../backbone')
  , Cocktail = require('backbone.cocktail')
  , RelatedTopicsView = require('./related_topics')
  , ZoteroDataView = require('./edit_zotero')
  , SaveItemMixin = require('./save_item_mixin')
  , DocumentView

module.exports = DocumentView = Backbone.View.extend({
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

    this.render();
  },

  render: function () {
    var that = this
      , template = require('../templates/document.html')

    this.$el.html( template({ doc: that.model }));
    this.topicListView.$el.appendTo( that.$('#document-related-topics') );
    this.zoteroView.$el.appendTo( that.$('#document-zotero-data') );
  }
});

Cocktail.mixin(DocumentView, SaveItemMixin);
