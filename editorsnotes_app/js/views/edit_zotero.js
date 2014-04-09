"use strict";

var Backbone = require('../backbone')
  , _ = require('underscore')
  , $ = require('../jquery')
  , CitationEngine = require('../utils/citation_generator')
  , zoteroToCsl = require('../utils/zotero_to_csl')
  , i18n = require('../utils/i18n')

module.exports = Backbone.View.extend({
  events: {
    'change .item-type-select': 'handleSelectItemType',
    'click .common-item-types a': 'handleSelectItemType',
    'click .add-creator': 'addCreator',
    'click .remove-creator': 'removeCreator',
    'input .zotero-entry': 'updateZoteroData'
  },

  initialize: function (opts) {
    this.citationEngine = new CitationEngine();
    this.renderedItemType = null;

    if (opts.zoteroData) {
      this.renderZoteroForm(opts.zoteroData);
    } else {
      this.fetchItemTypes().done(this.renderItemTypeSelect.bind(this));
    }
  },

  handleSelectItemType: function (e) {
    var itemType;
    e.preventDefault();

    if (e.type === 'change') {
      itemType = e.currentTarget.value;
    } else if (e.type === 'click') {
      itemType = $(e.currentTarget).data('item-type');
    }

    if (itemType) {
      this.fetchItemTemplate(itemType).done(this.renderZoteroForm.bind(this))
    }
  },

  fetchItemTypes: function () {
    return $.getJSON('/api/metadata/documents/item_types/');
  },

  fetchItemTemplate: function (itemType) {
    return $.getJSON('/api/metadata/documents/item_template/', { itemType: itemType });
  },

  renderItemTypeSelect: function (itemTypes) {
    var template = require('../templates/zotero_item_type_select.html');
    this.$el.html(template({ _: _, itemTypes: itemTypes }));
    this.$('select').prop('selectedIndex', -1);
  },

  renderZoteroForm: function (zoteroItem) {
    var template = require('../templates/zotero_item.html');
    this.$el.html(template({ _: _, data: zoteroItem, i18n: i18n.zotero }));
    this.renderedItemType = zoteroItem.itemType;
  },

  addCreator: function (e) {
    var $creator = $(e.currentTarget).closest('.zotero-creator');
    $creator.clone().insertAfter($creator).find('textarea').val('');
    return false;
  },

  removeCreator: function (e) {
    var $creator = $(e.currentTarget).closest('.zotero-creator');
    if ($creator.siblings('.zotero-creator').length) {
      $creator.remove();
    } else {
      $('textarea', $creator).val('');
    }
    return false;
  },

  updateZoteroData: function () {
    var zoteroData
      , citation

    zoteroData = this.formToObject();
    citation = this.citationEngine.makeCitation(zoteroToCsl(zoteroData));

    this.trigger('updatedZoteroData', zoteroData);
    this.trigger('updatedCitation', citation);
  },

  formToObject: function () {
    var zoteroObject = {};

    this.$('.zotero-entry').each(function (i, el) {
      var $field = $(el)
        , fieldKey = $field.data('zotero-key')

      if (fieldKey.substr(-2, 2) == '[]') {
        fieldKey = fieldKey.slice(0, -2);
        if (!zoteroObject[fieldKey]) zoteroObject[fieldKey] = [];
        zoteroObject[fieldKey].push((function () {
          var item = {};
          $('[data-zotero-attr]', $field).each(function (i, el) {
            item[el.getAttribute('data-zotero-attr')] = el.value;
          });
          return item;
        })());
      } else {
        zoteroObject[fieldKey] = $('textarea, input', $field).val();
      }
    });

    return zoteroObject;
  }
});
