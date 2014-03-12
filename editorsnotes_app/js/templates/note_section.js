var _ = require('underscore')
  , citationTemplate
  , noteReferenceTemplate
  , textTemplate

citationTemplate = _.template(''
  + '<div class="citation-side"><i class="icon-file"></i></div>'
  + ''
  + '<div class="citation-main">'
    + '<div class="citation-document">'
      + '<% if (ns.document) { print(ns.document_description) } %>'
    + '</div>'
    + '<div class="note-section-text-content"><%= ns.content %></div>'
  + '</div>')

noteReferenceTemplate = _.template(''
  + '<div class="note-reference-side"><i class="icon-pencil"></a></div>'
  + ''
  + '<div class="note-reference-main">'
    + '<div class="note-reference-note">'
      + '<% if (ns.note_reference) { print(ns.note_reference_title) } %>'
    + '</div>'
    + '<div class="note-section-text-content"><%= ns.content %></div>'
  + '</div>')

textTemplate = _.template(''
  + '<div class="note-section-text-content">'
    + '<%= ns.content %>'
  + '</div>')

module.exports = {
  'citation': citationTemplate,
  'note_reference': noteReferenceTemplate,
  'text': textTemplate
}
