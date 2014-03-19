"use strict";

var Backbone = require('../backbone')
  , $ = require('../jquery')
  , _ = require('underscore')

module.exports = Backbone.View.extend({
  events: {
    'click .add-section': function (e) { 
      e.preventDefault();
      this.createSection( $(e.currentTarget).data('section-type') ); 
    }
  },

  initialize: function (options) {
    var that = this;

    this.note = this.model; // alias to make things more sensible

    this._sectionViews = [];
    this.activeRequests = [];

    if (this.note.sections.length) {
      this.note.sections.forEach(this.addSection, this);
    }

    this.listenTo(this.note.sections, 'add', this.addSection);
    this.listenTo(this.note.sections, 'remove', this.removeSection);
    this.listenTo(this.note.sections, 'sync', this.saveOrder);

    this.listenTo(this.note.sections, 'deactivate', this.deactivateSections);

    this.note.once('sync', function () {
      that.listenTo(that.note, 'request', that.showLoader);
      that.listenTo(that.note.sections, 'request', that.showLoader);
    });


  },

  render: function () {
    var template = require('../templates/note_section_list.html')

    $('body').addClass('editing');

    this._rendered = true;
    this.$el.empty().html( template() );

    // jQuery element lookups to save for later
    this.$loader = this.$('img.loader');
    this.$statusMessage = this.$('.status-message');
    this.$sections = this.$('.note-section-list');

    this._sectionViews.forEach(function (sectionView) {
      this.$sections.append(sectionView.el);
    }, this);


    this.initSort();
    this.initDrag();
  },

  showLoader: function (model, xhr) {
    var that = this
      , $msg = this.$statusMessage.hide()
      , $loader = this.$loader.show()

    this.activeRequests.push(xhr);

    xhr.always(function () {
      that.activeRequests.pop(xhr);
      if (!that.activeRequests.length) {
        $loader.hide();
        $msg.show()
          .css('opacity', 1)
          .animate({ 'opacity': 1 }, 700)
          .animate({ 'opacity': 0})
      }
    });
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
        that.deactivateSections();
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
        if (ui.item.hasClass('add-section')) return;
        ui.item.show();
        that.saveOrder.call(that);
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
      helper: function (e, ui) {
        return $('<div class="drag-placeholder">')
          .html( $(this).html() )
          .css('width', that.$sections.innerWidth() - 22)
      },
      start: function (e, ui) {
        st = $(this).offsetParent().scrollTop();
      },
      drag: function (e, ui) {
        ui.position.top -= st;
      }
    });
  },

  createSection: function (sectionType, idx) {
    var _idx = idx || 0;

    // Sort is false because sections are ordered by the index of their ID in
    // the note's section_ordering field. Since this new section does not yet
    // have an ID, it can't be sorted.
    return this.note.sections.add(
      { 'section_type': sectionType }, 
      { at: _idx || 0, sort: false }
    ).at(_idx);
  },

  addSection: function (section) {
    var idx = section.collection.indexOf(section)
      , SectionView = require('./note_section')[section.get('section_type')]
      , view = new SectionView({ model: section })
      , target

    view.$el.data('sectionCID', view.model.cid);
    this._sectionViews.splice(idx, 0, view);

    if (!this._rendered) return;

    if (idx === 0) {
      this.$sections.prepend(view.el);
    } else {
      target = this.$sections.children()[idx - 1];
      view.$el.insertAfter(target);
    }

    if (section.isNew()) view.$el.trigger('click');
  },

  removeSection: function (section) {
    var that = this
      , sectionOrdering = this.note.get('section_ordering')
      , sectionViews = _(that._sectionViews)
      , viewToRemove

    viewToRemove = sectionViews.find(function (view) {
      return view.model === section
    });

    this._sectionViews = sectionViews.without(viewToRemove);

    sectionOrdering.pop(section.id);
    this.note.set('section_ordering', sectionOrdering);
  },

  deactivateSections: function (e) {
    var that = this;
    this._sectionViews.forEach(function (view) {
      view.deactivate.call(view);
    });
  },

  saveOrder: function () {
    var that = this
      , noteOrdering = this.note.get('section_ordering')
      , viewOrdering = []
      , renderedOrder

    renderedOrder = this.$sections.children('.note-section').map(function (idx, el) {
      return $(el).data('sectionCID');
    }).toArray();

    this._sectionViews.sort(function (a, b) {
      var idxa = renderedOrder.indexOf(a.model.cid)
        , idxb = renderedOrder.indexOf(b.model.cid)

      return idxa > idxb;
    });

    this._sectionViews.forEach(function (view) {
      if (view.model.id) viewOrdering.push(view.model.id);
    });

    if (noteOrdering.join('') !== viewOrdering.join('')) {
      this.note.set('section_ordering', viewOrdering);
      this.note.save();
    }
  }

});
