var EditorsNotes = {};

$(document).ready(function () {
  // Initialize timeago.
  $('time.timeago').timeago();

  $('#toggle-second-nav').click( function() {
    $(this).toggleClass('btn-primary');
    $('#bottom-nav').toggle();
  }); 

  var truncateChars = function(text, length) {
    var l = length || 100;
    return text.length < l ? text : 
      text.substr(0, l/2) + ' ... ' + text.substr(-(l/2));
  }

  var baseAutocompleteOptions = {
    source: function(request, response, x) {
      var targetModel = this.element.attr('search-target') || this.element.data('targetModel')
        , query = {'q': request.term}
        , projectSlug = this.element.data('projectSlug')
        , url = '/api/'
        , modelMap

      if (projectSlug) {
        url += ('projects/' + projectSlug + '/');
      }
      url += (targetModel + '/');

      console.log(this.element);

      modelMap = {
        topics: function (item) {
          var val = item.preferred_name;
          return { id: item.id, value: val, label: truncateChars(val), uri: item.uri };
        },
        notes: function (item) {
          var val = item.title;
          return { id: item.id, value: val, label: truncateChars(val), uri: item.uri };
        },
        documents: function (item) {
          var val = item.description;
          return { id: item.id, value: val, label: truncateChars(val), uri: item.uri };
        }
      }

      if (targetModel) {
        $.getJSON(url, query, function (data) {
          response($.map(data.results, modelMap[targetModel]));
        });
      } else {
        $.getJSON('/api/search/', { 'autocomplete': request.term }, function (data) {
          response($.map(data.results, function (item, index) {
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

        $('<i class="icon-remove-sign clear-search">')
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

  $('body').data('baseAutocompleteOptions', baseAutocompleteOptions);

  // Initialize autocomplete for search input box.
  $('input.search-autocomplete')
  .keydown(function(event) {
    // If no autocomplete menu item is active, submit on ENTER.
    if (event.keyCode == $.ui.keyCode.ENTER) {
      if ($('#ui-active-menuitem').length == 0) {
        $('#searchform form').submit();
      }
    }
  })
  .autocomplete(baseAutocompleteOptions)
  .data('ui-autocomplete')._renderItem = function (ul, item) {
    var $li = $.ui.autocomplete.prototype._renderItem.call(this, ul, item);

    $li.find('a').prepend('<strong>' + item.type + ': </strong>');
    return $li;
  }
});
