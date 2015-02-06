"use strict";

var OrderedCollectionView = require('../generic/ordered_collection_base')
  , $ = require('jquery')
  , CitationSectionView = require('../note/note_section').citation
  , CitationView

CitationView = CitationSectionView.extend({
  initialize: function () { this.render(); },
  render: function () {
    var template = require('../note/templates/note_section_citation.html')
      , citation = this.model
      , html

    html = template({ns: {
      'document': citation.get('document'),
      'document_description': citation.get('document_description'),
      'content': citation.get('notes')
    }});

    this.$el.html(html);
    this.afterRender();
  }
});

module.exports = OrderedCollectionView.extend({
  itemViewConstructor: CitationView,
  render: function () {
    var that = this
      , template = require('./templates/citation_list.html')

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
      distance: 1,
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
        $(this).animate({ 'opacity': 0 }, 120);
      },
      drag: function (e, ui) {
        ui.position.top = null;

        if (e.pageY < threshold) {
          ui.helper.css('top', e.pageY - 10);
        } else {
          ui.helper.show();
        }
      },
      stop: function () { 
        $(this).animate({ 'opacity': 1 }, 80);
      }
    });
  }
});
