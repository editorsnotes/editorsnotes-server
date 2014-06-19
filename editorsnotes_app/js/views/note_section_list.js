"use strict";

var OrderedCollectionView = require('./generic/ordered_collection_base')
  , $ = require('../jquery')

module.exports = OrderedCollectionView.extend({
  initialize: function () {
    $('body').addClass('editing');
    OrderedCollectionView.prototype.initialize.apply(this, arguments);
    if (this.collection.needsNormalization()) {
      this.collection.normalizeOrderingValues();
    }
  },
  render: function () {
    var that = this
      , template = require('../templates/note_section_list.html');

    this.$el.empty().html( template() );
    this.$itemsEl = this.$('.note-section-list');
    this.renderItems();
    this.initSort({
      stop: function (event, ui) {
        $(this).removeClass('sort-active');
        if (ui.item.hasClass('add-section')) {
          that.createSection(ui.item.data('section-type'), ui.item.index());
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
  makeItemView: function (section) {
    var SectionView = require('./note_section')[section.get('section_type')];
    return new SectionView({ model: section });
  },
  handleAddSectionButton: function (e) {
    e.preventDefault();
    this.createSection( $(e.currentTarget).data('section-type') ); 
  },
  createSection: function (sectionType, idx) {
    // Sort is false because sections are ordered by the index of their ID in
    // the note's section_ordering field. Since this new section does not yet
    // have an ID, it can't be sorted.
    return this.collection.add(
      { section_type: sectionType },
      { at: idx }
    );
  },

  initStickyBar: function () {
    var $window = $(window)
      , $barContainer = this.$('#section-add-bar-container')
      , $bar = $barContainer.find('#citation-edit-bar')

    $window
      .off('scroll.note-section-list')
      .on('scroll.note-section-list', function () {
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
      drag: function (e, ui) {
        ui.position.top = null;

        if (e.pageY < threshold) {
          ui.helper.css('top', e.pageY - 10);
        } else {
          ui.helper.show();
        }
      },
      start: function () {
        threshold = $('.note-section-list').offset().top;
      }
    });
  }
});
