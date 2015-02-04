"use strict";

var $ = require('../jquery')
  , _ = require('underscore')
  , ALLOWED_MODELS = ['topics', 'documents', 'notes']

// Return a function which will translate a given item into the representation
// that jquery.ui.autocomplete expects.
function reprForModel(model) {
  var valMap = { 'topics': 'preferred_name', 'notes': 'title', 'documents': 'description' }
    , valField = valMap[model]

  function repr(item) {
    var val = item[valField];
    return { id: item.id, value: val, label: val, uri: item.uri }
  }

  return repr
}


function ModelCompleter(el, project, model, opts) {
  var $el;

  if (!project) throw('Must pass project slug to function.');
  if (!_.contains(ALLOWED_MODELS, model)) throw('Invalid model.');

  $el = el ? $(el) : $('<input type="text">');
  if (!$el.is('input[type="text"]')) throw ('Element must be a text input.');

  this.project = project;
  this.model = model;
  this.$el = $el;
  this.url = '/api/projects/' + project + '/' + model + '/';
  this.opts = opts;

  this.enable();
}

ModelCompleter.prototype = {
  getOpts: function () {
    var that = this;
    return _.extend({
      minLength: 2,
      source: function(request, response) {
        $.getJSON(that.url, that.buildQuery(request.term), function (data) {
          var results = _.map(data.results, reprForModel(that.model));
          response([{'count': data.count}].concat(results));
        });
      },
      open: function () {
        var autocomplete, ul;
        if (that.$countEl) {
          autocomplete = that.$el.data('ui-autocomplete');
          ul = that.$el.data('ui-autocomplete').menu.element;
          ul.prepend(that.$countEl);
          ul.position($.extend({ of: autocomplete.element }, autocomplete.options.position ));
        }
      }
    }, that.opts)
  },
  buildQuery: function (term) {
    return { 'q': term };
  },
  enable: function () {
    var that = this
      , opts = this.getOpts();

    this.$el.autocomplete(opts);
    this.$el.prop('placeholder', 'Begin typing to search for ' + that.model + '.');
    this.$el.data('ui-autocomplete')._renderItem = function (ul, item) {
      return $('<li>')
        .data('ui-autocomplete-item', item)
        .append('<a>' + item.label + '</a>')
        .appendTo(ul);
    }
    this.$el.data('ui-autocomplete')._renderMenu = function (ul, items) {
      var shownCount = items.length
        , actualCount
        , resultstxt

      if (items.length && items[0].hasOwnProperty('count')) {
        actualCount = items.splice(0, 1)[0].count;
        shownCount = shownCount - 1;
        resultstxt = actualCount > 0 ? (shownCount + ' out of ' + actualCount) : 'No';
        resultstxt += ' result' + (actualCount != 1 ? 's' : '') + '.';
        that.$countEl = $('<li class="ui-autocomplete-header">')
          .html('<a>' + resultstxt + '</a>');
      }
      $.ui.autocomplete.prototype._renderMenu.call(this, ul, items);
    }
  },
  disable: function () {
    this.$el.autocomplete('destroy');
    this.$el.prop('placeholder', '');
  }
}

module.exports = ModelCompleter;
