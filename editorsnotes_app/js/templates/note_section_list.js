var _ = require('underscore');

module.exports = _.template(''
  + '<div id="citation-edit-bar">'
    + '<h4>Add section: </h4>'
    + '<a class="add-section" data-section-type="citation">'
      + '<i class="icon-file"></i> Citation'
    + '</a>'
    + '<a class="add-section" data-section-type="text">Text</a>'
    + '<a class="add-section" data-section-type="note_reference">'
      + '<i class="icon-pencil"></i> Note reference'
    + '</a>'
    + '<span class="status-message">All changes saved.</span>'
    + '<img class="loader" src="/static/style/icons/ajax-loader.gif">'
  + '</div>'
  + '<div class="note-section-list"></div>')
