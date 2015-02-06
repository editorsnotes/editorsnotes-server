"use strict";

var _ = require('underscore')
  , $ = require('../../jquery')
  , Backbone = require('../../backbone')
  , Cocktail = require('backbone.cocktail')
  , RelatedTopicsView = require('../widgets/related_topics')
  , ZoteroDataView = require('./zotero')
  , ScanListView = require('./scan_list')
  , SaveItemMixin = require('../generic/save_item_mixin')
  , HandleErrorMixin = require('../generic/handle_error_mixin')
  , DocumentView

module.exports = DocumentView = Backbone.View.extend({
  events: {
    'click .js-edit-manually': 'editCitationManually',
    'click .js-generate-citation': 'generateCitation'
  },

  initialize: function () {
    var that = this;

    this.topicListView = new RelatedTopicsView({ collection: that.model.relatedTopics });
    this.scanListView = new ScanListView({ collection: that.model.scans });
    this.zoteroView = new ZoteroDataView({ zoteroData: that.model.get('zotero_data') });

    this.listenTo(this.zoteroView, 'updatedZoteroData', function (data) {
      data = _.isEmpty(data) ? null : data;
      that.model.set('zotero_data', data);
    });

    this.listenToOnce(this.zoteroView, 'rendered', function () {
      if (
        that.model.isNew() ||
        $(that.model.get('description')).text() === that.zoteroView.updateZoteroData().citation
      ) {
        this.generateCitation();
      } else {
        this.editCitationManually();
      }
    });

    this.render();
  },

  render: function () {
    var that = this
      , template = require('./templates/document.html')

    this.$el.html( template({ doc: that.model }));
    this.topicListView.$el.appendTo( that.$('#document-related-topics') );
    this.zoteroView.$el.appendTo( that.$('#document-zotero-data') );

    if (!this.model.isNew()) {
      this.scanListView.$el.appendTo( that.$('#document-scans') );
    }

    this.$citationEditToggle = this.$('#document-citation button');
  },

  editCitationManually: function () {
    var that = this;

    this.$citationEditToggle.show()
      .removeClass('js-edit-manually')
      .addClass('js-generate-citation')
      .text('Generate from metadata')

    this.stopListening(this.zoteroView, 'updatedCitation');
    this.$('#printed-citation')
      .html('')
      .on('editor:input', function (e, val) {
        that.model.set('description', val);
      })
      .editText({
        initialValue: that.model.get('description'),
        toolbarType: 'minimal',
        height: 50
      });

    return false;
  },

  generateCitation: function () {
    var that = this
      , citation = this.$('#printed-citation')

    if ('editor' in citation.data()) {
      this.$('#printed-citation')
        .off('editor:input')
        .editText('destroy');
    }

    this.$citationEditToggle.show()
      .removeClass('js-generate-citation')
      .addClass('js-edit-manually')
      .text('Edit manually')

    this.listenTo(this.zoteroView, 'updatedCitation', function (data) {
      if (data) {
        that.$('#printed-citation').html(data);
      } else {
        that.$('#printed-citation').html(
          '<span class="quiet">Enter document metadata to generate a citation</span>');
      }
      that.model.set('description', data);
    });

    this.zoteroView.updateZoteroData();

    return false;
  }
});

Cocktail.mixin(DocumentView, SaveItemMixin, HandleErrorMixin);
