"use strict";

var Backbone = require('../backbone')
  , _ = require('underscore')
  , $ = require('../jquery')
  , CitationEngine = require('../utils/citation_generator')
  , zoteroToCsl = require('../utils/zotero_to_csl')
  , i18n = require('../utils/i18n')

function fetchItemTypes() {
  return $.getJSON('/api/metadata/documents/item_types/');
}

function fetchItemTemplate(itemType) {
  return $.getJSON('/api/metadata/documents/item_template/', { itemType: itemType });
}

function fetchCreatorTypes(itemType) {
  return $.getJSON('/api/metadata/documents/item_type_creators/', { itemType: itemType });
}


module.exports = Backbone.View.extend({
  events: {
    'change .item-type-select': 'handleSelectItemType',
    'click .common-item-types a': 'handleSelectItemType',
    'click .add-creator': 'addCreator',
    'click .remove-creator': 'removeCreator',
    'click .toggle-creator-field': 'toggleCreatorField',
    'input': 'updateZoteroData',
    'change select': 'updateZoteroData'
  },

  initialize: function (opts) {
    this.citationEngine = new CitationEngine();
    this.renderedItemType = null;

    // If passed data, render data editing form. Otherwize, render a form to
    // select the item type first.
    if (opts && opts.zoteroData) {
      this.renderZoteroForm(opts.zoteroData);
    } else {
      fetchItemTypes().done(this.renderItemTypeSelect.bind(this));
    }
  },

  renderItemTypeSelect: function (itemTypes) {
    var template = require('../templates/zotero_item_type_select.html');
    this.$el.html(template({ _: _, itemTypes: itemTypes }));
    this.$('select').prop('selectedIndex', -1);
  },

  renderZoteroForm: function (zoteroItem) {
    var that = this
      , template = require('../templates/zotero_item.html')

    fetchCreatorTypes(zoteroItem.itemType).done(function (creatorTypes) {
      that.$el.html(template({
          _: _,
        data: zoteroItem,
        i18n: i18n.zotero,
        creatorTypes: creatorTypes
      }));
    });
    this.renderedItemType = zoteroItem.itemType;

  },

  handleSelectItemType: function (e) {
    var itemType = e.type === 'change' ?
      e.currentTarget.value
      : $(e.currentTarget).data('item-type');

    // Fetch an empty item template
    if (itemType) fetchItemTemplate(itemType).done(this.renderZoteroForm.bind(this));

    return false;
  },

  addCreator: function (e) {
    var $creator = $(e.currentTarget).closest('.zotero-entry');
    $creator.clone().insertAfter($creator).find('input').val('');
    this.$el.trigger('input');
    return false;
  },

  removeCreator: function (e) {
    var $creator = $(e.currentTarget).closest('.zotero-entry');
    if ($creator.siblings('.zotero-creator').length) {
      $creator.remove();
    } else {
      $('input', $creator).val('');
    }
    this.$el.trigger('input');
    return false;
  },

  toggleCreatorField: function (e) {
    var $creator = $(e.currentTarget).closest('.zotero-entry')
      , $inputs = $creator.find('input')
      , val

    if ($inputs.length > 1) {
      // Switch to single field
      val = _($inputs.toArray()).chain().pluck('value').filter(Boolean).value().join(' ');
      $('<input data-zotero-attr="name" placeholder="Full name" value="' + val + '">').insertBefore($inputs.first());
      $inputs.remove();
    } else {
      // Switch to multiple fields
      val = $inputs.val().split(' ');
      $('<input data-zotero-attr="lastName" placeholder="Family (last) name" value="' + (val.pop() || '') + '">')
        .insertAfter($inputs);
      $('<input data-zotero-attr="firstName" placeholder="Given (first) name" value="' + val.join(' ') + '">')
        .css('margin-right', '3px')
        .insertAfter($inputs);
      $inputs.remove();
      
    }
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
