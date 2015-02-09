"use strict";

var $ = require('./jquery')
  , Backbone = window.Backbone = require('./backbone')
  , BaseRouter

$(document).ready(function () {
  initTimeago();
  initTooltips();
  initAutocomplete();

  window.EditorsNotes.base = new BaseRouter();
});

BaseRouter = Backbone.Router.extend({
  routes: {}
});

// Initialize timeago
function initTimeago() {
  $('time.timeago').timeago();
}

// Initialize autocomplete for search input box
function initAutocomplete() {
  var opts = require('./utils/base_autocomplete_opts');

  $('input.search-autocomplete')
  .keydown(function(event) {
    // If no autocomplete menu item is active, submit on ENTER.
    if (event.keyCode === $.ui.keyCode.ENTER) {
      if ($('#ui-active-menuitem').length === 0) {
        $('#searchform form').submit();
      }
    }
  })
  .autocomplete(opts)
  .data('ui-autocomplete')._renderItem = function (ul, item) {
    var $li = $.ui.autocomplete.prototype._renderItem.call(this, ul, item);

    $li.find('a').prepend('<strong>' + item.type + ': </strong>');
    return $li;
  }
}

// Initialize tooltip functionality
function initTooltips () {
  $('body')
    .tooltip({ selector: '[data-toggle="tooltip"]' })
    .on('click', 'a[data-toggle="tooltip"][href="#"]', function () { return false });
}
