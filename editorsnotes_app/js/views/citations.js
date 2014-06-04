"use strict";

var Backbone = require('../backbone')

module.exports = Backbone.View.extend({
  initialize: function () {
    this.render();
  },
  render: function () {
    var template = require('../templates/note_section_citation.html')
      , els

    els = this.collection.map(function (citation) {
      return '<div class="note-section">' + template({
        ns: {
          'document': citation.get('document'),
          'document_description': citation.get('document_description'),
          'content': citation.get('notes')
        }
      }) + '</div>';
    });
    this.$el.html(els.join(''));
  }
});
