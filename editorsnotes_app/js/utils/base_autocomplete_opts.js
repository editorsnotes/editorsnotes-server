"use strict";

var $ = require('../jquery')
  , truncateChars = require('./truncate_chars')
  , valMap = { topics: 'preferred_name', notes: 'title', documents: 'description' }

// Return a function which will translate a given item into the representation
// that jquery.ui.autocomplete expects.
function reprForModel(model) {
  var val = valMap[model];

  function repr(item) {
    var _val = item[val]
    return {
      id: item.id,
      value: _val,
      label: truncateChars(_val),
      uri: item.uri
    }
  }

  return repr
}

module.exports = {
  source: function(request, response) {
    var targetModel = this.element.attr('search-target') || this.element.data('targetModel')
      , query = {'q': request.term}
      , projectSlug = this.element.data('projectSlug')
      , url = '/api/'

    if (projectSlug) {
      url += ('projects/' + projectSlug + '/');
    }
    url += (targetModel + '/');

    if (targetModel) {
      $.getJSON(url, query, function (data) {
        response($.map(data.results, reprForModel(targetModel)));
      });
    } else {
      $.getJSON('/api/search/', { 'autocomplete': request.term }, function (data) {
        response($.map(data.results, function (item) {
          var val = item.title
            , type = item.type.slice(0,1).toUpperCase() + item.type.slice(1)

          return { type: type, value: val, label: truncateChars(val), uri: item.url }
        }));
      });
    }

  },
  minLength: 2,
  select: function(event, ui) {
    var $this = $(event.target);
    if (ui.item && !$this.hasClass('autocomplete-no-redirect')) {
      location.href = ui.item.uri;
    } else if (ui.item) {

      /*
       * my god, what does this even do? Please take it out ASAP.
       */

      var selectedItem = $('<div style="position: absolute; left: -9999px">').html(ui.item.value).appendTo('body'),
        newWidth = selectedItem.innerWidth() + 5 ;

      newWidth = newWidth > 700 ? 700 : newWidth;

      if (!$this.data('originalWidth')) {
        $this.data({
          'originalWidth': $this.innerWidth(),
          'selectSibling': $this.siblings('select')
        });
      }
      selectedItem.remove();

      $this
        .attr('readonly', 'true')
        .css('width', newWidth + 5 + 'px')
        .blur();

      if ($this.data('selectSibling').length > 0) {
        $this.data('selectSibling').attr('disabled', 'disabled');
      }

      $('<input type="hidden">').attr({
        'name': 'autocomplete-model',
        'value': $this.attr('search-target')
      }).insertAfter($this);
      $('<input type="hidden">').attr({
        'name': 'autocomplete-id',
        'value': ui.item.id
      }).insertAfter($this);

      $('<i class="fa fa-times-circle clear-search">')
        .css({
          'margin-left': '6px',
          'cursor': 'pointer'
        })
        .insertAfter($this)
        .click(function() {
          var $this = $(this),
            $searchBar = $this.prev('input.search-autocomplete');
          $searchBar
            .removeAttr('readonly')
            .css('width', $searchBar.data('originalWidth') + 'px')
            .val('')
            .siblings('input[type="hidden"][name^="autocomplete-"]').remove();
          if ($searchBar.data('selectSibling').length > 0) {
            $searchBar.data('selectSibling').removeAttr('disabled');
          }
          $this.remove();
        });
    }
  }
}
