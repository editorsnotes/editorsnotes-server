"use strict";

var Backbone = require('../backbone')
  , $ = require('../jquery')
  , _ = require('underscore')

function makeSectionView(section) {
  var SectionView = require('./note_section')[section.get('section_type')];
  return new SectionView({ model: section });
}

module.exports = Backbone.View.extend({
  events: {
    'click .add-section': function (e) { 
      e.preventDefault();
      this.createSection( $(e.currentTarget).data('section-type') ); 
    }
  },

  initialize: function () {
    this._sectionViews = this.model.sections.map(makeSectionView);

    $('body').addClass('editing');
    
    this.listenTo(this.model.sections, 'add', this.addSection);
    this.listenTo(this.model.sections, 'remove', this.removeSection);

    this.render();
  },

  render: function () {
    var template = require('../templates/note_section_list.html');
    this.$el.empty().html( template() );

    this.$sections = this.$('.note-section-list');
    this.renderSections();

    this.initSort();
    this.initDrag();
  },

  renderSections: function (update) {
    var $sections = this.$sections
      , views = this._sectionViews
      
    if (update) {
      // Only append elements that are unattached
      _(views).chain().filter(function (view) {
        var attached = !!view.$el.closest(document.documentElement);
        return attached;
      }).forEach(function (view) {
        var idx = _.indexOf(views, view);
        if (idx === 0) {
          view.$el.prependTo($sections);
        } else {
          view.$el.insertAfter(views[idx - 1].$el);
        }
      });
    } else {
      // Append all view elements
      this.$sections.append(_.pluck(this._sectionViews, 'el'));
    }

  },

  sortSectionViews: function () {
    this._sectionViews.sort(function (a, b) {
      return a.model.get('ordering') - b.model.get('ordering');
    });
  },

  addSection: function (section) {
    var view = makeSectionView(section);
    this._sectionViews.push(view);
    this.sortSectionViews();
    this.renderSections(true);
    if (section.isNew()) view.$el.trigger('click');
  },

  createSection: function (sectionType, idx) {
    // Sort is false because sections are ordered by the index of their ID in
    // the note's section_ordering field. Since this new section does not yet
    // have an ID, it can't be sorted.
    return this.model.sections.add(
      { section_type: sectionType },
      { at: idx }
    );
  },

  removeSection: function (section) {
    var sectionViews = _(this._sectionViews)
      , viewToRemove

    viewToRemove = sectionViews.find(function (view) {
      return view.model === section
    });

    this._sectionViews = sectionViews.without(viewToRemove);
  },

  initSort: function () {
    var that = this;
    this.$sections.sortable({
      placeholder: 'section-placeholder',
      cancel: 'input,textarea,button,select,option,.note-section-edit-active',
      cursor: 'pointer',
      cursorAt: { 'left': 200, 'top': 20 },
      axis: 'y',
      tolerance: 'pointer',
      helper: function (event, item) {
        return $(item).clone().addClass('active').css({
          'max-height': '120px',
          'border': 'none',
          'opacity': 0.75
        });
      },
      start: function (event, ui) {
        $(this).addClass('sort-active');
        ui.item.hide();
        that.$sections.sortable('refreshPositions');
      },
      stop: function (event, ui) {
        $(this).removeClass('sort-active');
        if (ui.item.hasClass('add-section')) {
          that.createSection(ui.item.data('section-type'), ui.item.index());
          ui.item.remove();
        }
      },
      update: function (event, ui) {
        var section, ordering, origIdx, newIdx;

        if (ui.item.hasClass('add-section')) return;
        ui.item.show();

        section = that.model.sections.get(ui.item.data('cid'));

        origIdx = section.collection.indexOf(section);
        newIdx = ui.item.index();
        if (origIdx === newIdx) return;
        if (newIdx > origIdx) newIdx += 1;

        ordering = section.collection.getIntermediateOrderingValue(newIdx);
        section.set('ordering', Math.floor(ordering));
        section.save();
      }
    });
  },

  initDrag: function () {
    var that = this
      , $addBar = this.$('#citation-edit-bar').css('overflow', 'auto')
      , st

    $('.add-section', $addBar).draggable({
      axis: 'y',
      distance: 10,
      appendTo: $addBar,
      connectToSortable: that.$sections,
      helper: function () {
        return $('<div class="drag-placeholder">')
          .html( $(this).html() )
          .css('width', that.$sections.innerWidth() - 22)
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
