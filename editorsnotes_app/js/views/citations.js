"use strict";

var OrderedCollectionView = require('./generic/ordered_collection_base')
  , $ = require('jquery')
  , CitationView = require('./citation')

module.exports = OrderedCollectionView.extend({
  itemViewConstructor: CitationView,
  render: function () {
    var that = this
      , template = require('../templates/citation_list.html')

    this.$el.empty().html( template() );
    this.$itemsEl = this.$('.citation-list');
    this.renderItems();
    this.$el.closest('body').addClass('editing');
    this.initSort({
      stop: function (event, ui) {
        $(this).removeClass('sort-active');
        if (ui.item.hasClass('add-section')) {
          that.collection.add({}, { at: ui.item.index() });
          ui.item.remove();
        }
      }
    });
    this.initDrag();
    this.initStickyBar();
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

  initStickyBar: function () {
    var $window = $(window)
      , $barContainer = this.$('#section-add-bar-container')
      , $bar = $barContainer.find('#citation-edit-bar')

    $window
      .off('scroll.citation-list')
      .on('scroll.citation-list', function () {
        var scrollTop = $window.scrollTop()
          , offsetTop = $barContainer.offset().top

        if (scrollTop > offsetTop) {
          $bar.addClass('sticky');
        } else {
          $bar.removeClass('sticky');
        }
      });
  },

  initDrag: function () {
    var that = this
      , $addBar = this.$('#citation-edit-bar').css('overflow', 'auto')
      , threshold

    $('.add-section', $addBar).draggable({
      axis: 'y',
      distance: 2,
      appendTo: $addBar.parent(),
      cursor: 'move',
      connectToSortable: that.$itemsEl,
      helper: function () {
        return $('<div class="drag-placeholder">')
          .html( $(this).html() )
          .css('width', that.$itemsEl.innerWidth() - 22)
      },
      start: function () {
        threshold = $('.citation-list').offset().top;
      },
      drag: function (e, ui) {
        ui.position.top = null;

        if (e.pageY < threshold) {
          ui.helper.css('top', e.pageY - 10);
        } else {
          ui.helper.show();
        }
      }
    });
  }
});
