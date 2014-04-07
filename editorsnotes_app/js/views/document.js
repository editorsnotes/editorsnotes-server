"use strict";

var Backbone = require('../backbone')
  , RelatedTopicsView = require('./related_topics')
  , ZoteroDataView = require('./edit_zotero')

module.exports = Backbone.View.extend({
  initialize: function (options) {
    var that = this;

    this.topicListView = new RelatedTopicsView({ collection: that.model.relatedTopics });

    this.zoteroView = new ZoteroDataView({ zoteroData: that.model.get('zotero_data') });
    this.listenTo(this.zoteroView, 'updatedCitation', function (data) {
      that.$('#document-citation').html(data);
    });

  },

  render: function () {
    var that = this
      , template = require('../templates/document.html')

    this.$el.html(template({ doc: that.model }));

    this.topicListView.$el.appendTo( that.$('#document-related-topics') );
    this.zoteroView.$el.appendTo( that.$('#document-zotero-data') );
  }

});
