"use strict";

var OrderedCollectionView = require('./generic/ordered_collection_base')
  , $ = require('jquery')
  , CitationView = require('./citation')

module.exports = OrderedCollectionView.extend({
  itemViewConstructor: CitationView,
  events: {
    'click .add-citation': 'handleAddCitationButton'
  },
  render: function () {
    var that = this
      , template = require('../templates/citation_list.html')

    this.$el.empty().html( template() );
    this.$itemsEl = this.$('.citation-list');
    this.renderItems();
    this.initDrag();
    this.initSort({
      stop: function (event, ui) {
        $(this).removeClass('sort-active');
        if (ui.item.hasClass('add-citation')) {
          that.collection.add({}, { at: ui.item.index() });
          ui.item.remove();
        }
      }
    });
  },
  onAddItemView: function (view) {
    if (view.model.isNew()) {
      view.edit();
    }
  },
  handleAddCitationButton: function (e) {
    e.preventDefault();
    this.collection.add({});
  },
  initDrag: function () {
    var that = this
      , $addBar = this.$('#citation-edit-bar').css('overflow', 'auto')
      , st

    $('.add-citation', $addBar).draggable({
      axis: 'y',
      distance: 10,
      appendTo: $addBar,
      connectToSortable: that.$itemsEl,
      helper: function () {
        return $('<div class="drag-placeholder">')
          .html( $(this).html() )
          .css('width', that.$itemsEl.innerWidth() - 22)
      },
      start: function () {
        st = $(this).offsetParent().scrollTop();
      },
      drag: function (e, ui) {
        ui.position.top -= st;
      }
    });
  }
});
