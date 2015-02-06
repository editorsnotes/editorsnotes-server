"use strict";

/*
 * Base view for selecting items. Includes an autocomplete input and a button
 * to launch a modal for adding an item inline. Inheriting views must define
 * an `addItem` method to handle creating & rendering that modal.
 *
 * Options:
 *    project (required): slug of the project currently being worked on
 *    autocompleteopts: object defining settings for the autocomplete input
 */

var Backbone = require('../../backbone')
  , $ = require('../../jquery')
  , _ = require('underscore')

module.exports = Backbone.View.extend({
  events: {
    'click .add-new-object': 'addItem'
  },
  initialize: function (options) {
    var that = this
      , url

    this.project = options.project;
    url = this.autocompleteURL.call(this)

    this._autocompleteopts = _.extend({
      select: that.selectItem.bind(that),
      appendTo: '#note-sections',
      minLength: 2,
      messages: {
        noResults: '',
        results: function () { return; }
      },
      source: function (request, response) {
        $.getJSON(url, {'q': request.term}, function (data) {
          response(data.results.map(function (item) {
            item.label = item[that.labelAttr || 'title'];
            return item;
          }));
        });
      },
    }, that.autocompleteopts || {})

    this.render();
  },
  render: function () {
    var that = this
      , template = require('./templates/add_or_select_item.html')
      , $input

    this.$el.html(template({type: that.type}));

    $input = this.$('input');
    $input.autocomplete(that._autocompleteopts)
      .data('ui-autocomplete')._renderItem = function (ul, item) {
        return $('<li>')
          .data('ui-autocomplete-item', item)
          .append('<a>' + item.label + '</a>')
          .appendTo(ul)
      }
  }
});

