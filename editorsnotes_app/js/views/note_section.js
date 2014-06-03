"use strict";

var Backbone = require('../backbone')
  , $ = require('../jquery')
  , NoteSectionView
  , CitationSectionView
  , NoteReferenceSectionView
  , TextSectionView

/*
 * Base view for all note sections. Children must define the following methods:
 *
 * `isEmpty`
 */

NoteSectionView = Backbone.View.extend({
  tagName: 'div',
  className: 'note-section',
  isActive: false,

  events: { 'click': 'edit' },

  initialize: function () {
    var that = this;

    this.render();
    this.$el.addClass('note-section-' + this.model.get('section_type'));
    this.$el.data('cid', that.model.cid);
  },

  render: function () {
    var that = this
      , sectionType = this.model.get('section_type')
      , template = require('../templates/note_section')[sectionType]

    this.$el.html( template({ns: that.model.toJSON()}) );
    this.afterRender && this.afterRender.call(this);
  },

  edit: function () {
    var that = this
      , html

    if (this.isActive) return;

    this.model.collection.trigger('deactivate');

    this.isActive = true;
    this.$el.addClass('note-section-edit-active');
    this.$('.note-section-text-content').editText({
      initialValue: that.model.get('content'),
      destroy: function (val) {
        $(this).html(val);
        that.model.set('content', val);
        that.$('.edit-row').remove();
      }
    });

    html = ''
      + '<div class="edit-row row">'
        + '<a class="btn btn-primary save-section pull-right">Save</a>'
        + '<a class="btn btn-danger delete-section">Delete section</a>'
      + '</div>'

    $(html)
      .appendTo(this.$el)
      .on('click .btn', function (e) {
        var deleteSection = $(e.target).hasClass('delete-section');
        setTimeout(function () { that.deactivate.call(that, deleteSection); }, 10);
      });

    return;
  },

  deactivate: function (deleteModel) {
    var collection;

    if (!this.isActive) return;

    this.isActive = false;
    this.$el.removeClass('note-section-edit-active');
    this.$('.note-section-text-content').editText('destroy');

    if (this.isEmpty() || deleteModel) {
      collection = this.model.collection
      this.remove();
      this.model.destroy({
        success: function (model) {
          collection.remove(model);
          collection.trigger('removeEmpty');
        }
      });
    } else {
      this.model.save();
    }

    return;
  },
  
});

CitationSectionView = NoteSectionView.extend({
  afterRender: function () {
    var that = this
      , SelectDocumentView = require('./select_document')
      , documentSelect = new SelectDocumentView({ project: this.model.project })
      , $documentContainer

    if (!this.model.isNew()) return;

    $documentContainer = this.$('.citation-document').html(documentSelect.el);

    this.listenToOnce(documentSelect, 'documentSelected', function (doc) {
      $documentContainer.html(doc.get('description'));
      that.model.set('document_description', doc.get('description'));
      that.model.set('document', doc.url());
      documentSelect.remove();
    });

  },
  isEmpty: function () { return !this.model.has('document') }
});

NoteReferenceSectionView = NoteSectionView.extend({
  afterRender: function () {
    var that = this
      , SelectNoteView = require('./select_note')
      , noteSelect = new SelectNoteView({ projet: this.model.project })
      , $noteContainer

    if (!this.model.isNew()) return;

    $noteContainer = this.$('.note-reference-note-container')
      .html(noteSelect.el);

    this.listenToOnce(noteSelect, 'noteSelected', function (note) {
      $noteContainer.html(note.get('title'));
      that.model.set('note_reference', note.url());
      that.model.set('note_reference_title', note.get('title'));
      noteSelect.remove();
    });
  },
  isEmpty: function () { return !this.model.has('note_reference') }
});

TextSectionView = NoteSectionView.extend({
  isEmpty: function () { return !this.model.get('content') }
});

module.exports = {
  citation: CitationSectionView,
  note_reference: NoteReferenceSectionView,
  text: TextSectionView
}
