"use strict";

var Backbone = require('../backbone')
  , $ = require('../jquery')

module.exports = Backbone.View.extend({
  events: {
    'change .item-type-select': function (e) {
      this.renderZoteroForm(e.currentTarget.value);
    },
    'click .common-item-types li': function (e) {
      e.preventDefault();
      this.renderZoteroForm($('a', e.currentTarget).data('item-type'));
    },
    'click .add-creator': 'addCreator',
    'click .remove-creator': 'removeCreator',
    'input .zotero-entry': 'sendZoteroData',
  },

  initialize: function () {
    var that = this

    this.citeprocWorker = new Worker('/static/function/citeproc-worker.js');
    this.citeprocWorker.addEventListener('message', function (e) {
      that.trigger('citationUpdated', e.data.citation);
    });

    this.render();

    $.getJSON('/api/document/itemtypes/')
      .done(function (itemTypes) {
        var template = require('../templates/zotero_item_type_select.html')
          , select = template(itemTypes)

        that.$el.html('<hr />' + select);
        that.$('select').prop('selectedIndex', -1);
      })
      .error(function () {
        console.error('Could not fetch item types from server.');
      });
  },

  renderZoteroForm: function (itemType) {
    var that = this
      , $input = this.$('input').hide()

    $.get('/api/document/template/?itemType=' + itemType)
      .done(function (template) {
        var $template = $(template).filter('#zotero-information-edit');

        that.$el
          .html('<hr />' + $template.html())
          .find('.zotero-entry-delete').remove();
      })
      .fail(function () {
        alert('Could not retrieve template');
        $input.show()
      });
  },

  addCreator: function (e) {
    var $creator = $(e.currentTarget).closest('.zotero-creator');

    e.preventDefault();
    $creator.clone().insertAfter($creator).find('textarea').val('');
  },

  removeCreator: function (e) {
    var $creator = $(e.currentTarget).closest('.zotero-creator')

    e.preventDefault();
    $creator.siblings('.zotero-creator').length ?
      $creator.remove() :
      $('textarea', $creator).val('')
  },

  getZoteroData: function () {
    return EditorsNotes.zotero.zoteroFormToObject(this.$el);
  },

  sendZoteroData: function () {
    var that = this;

    this.citeprocWorker.postMessage({
      zotero_data: that.getZoteroData()
    });
  },
});
