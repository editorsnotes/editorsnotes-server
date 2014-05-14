"use strict";

var Backbone = require('../backbone')
  , Cocktail = require('backbone.cocktail')
  , RelatedTopicsView = require('./related_topics')
  , ZoteroDataView = require('./edit_zotero')
  , ScanListView = require('./scan_list')
  , SaveItemMixin = require('./save_item_mixin')
  , DocumentView

module.exports = DocumentView = Backbone.View.extend({
  initialize: function (options) {
    var that = this;

    this.topicListView = new RelatedTopicsView({ collection: that.model.relatedTopics });
    this.scanListView = new ScanListView({ collection: that.model.scans });

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
    this.scanListView.$el.appendTo( that.$('#document-scans') );
  }
});

Cocktail.mixin(DocumentView, SaveItemMixin);
