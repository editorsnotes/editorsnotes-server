"use strict";
var CitationSectionView = require('./note_section').citation

module.exports = CitationSectionView.extend({
  initialize: function () { this.render(); },
  render: function () {
    var template = require('../templates/note_section_citation.html')
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
