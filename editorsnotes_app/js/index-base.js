"use strict";

var $ = require('./jquery')
  , EditorsNotes = window.EditorsNotes

EditorsNotes.baseAutocompleteOpts = require('./utils/base_autocomplete_opts');

$(document).ready(function () {

  // Initialize timeago
  $('time.timeago').timeago();

  // Initialize autocomplete for search input box
  $('input.search-autocomplete')
  .keydown(function(event) {
    // If no autocomplete menu item is active, submit on ENTER.
    if (event.keyCode === $.ui.keyCode.ENTER) {
      if ($('#ui-active-menuitem').length === 0) {
        $('#searchform form').submit();
      }
    }
  })
  .autocomplete(EditorsNotes.baseAutocompleteOpts)
  .data('ui-autocomplete')._renderItem = function (ul, item) {
    var $li = $.ui.autocomplete.prototype._renderItem.call(this, ul, item);

    $li.find('a').prepend('<strong>' + item.type + ': </strong>');
    return $li;
  }

  $('body')
    .tooltip({ selector: '[data-toggle="tooltip"]' })
    .on('click', 'a[data-toggle="tooltip"][href="#"]', function () { return false });

});
