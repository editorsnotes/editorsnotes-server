"use strict";

var Backbone = require('../../backbone')
  , _ = require('underscore')
  , $ = require('../../jquery')

// "ordering" field is hardcoded. It could be made generic.

module.exports = Backbone.View.extend({
  initialize: function () {
    this._itemViews = this.collection.map(this._makeItemView, this);
    this.listenTo(this.collection, 'add', this.addItem);
    this.listenTo(this.collection, 'remove', this.removeItem);
  },
  _makeItemView: function (item) {
    var view;

    if (_.isFunction(this.makeItemView)) {
      view = this.makeItemView(item);
    } else if ('itemViewConstructor' in this) {
      view = new this.itemViewConstructor({ model: item });
    } else {
      throw ('Ordered collection views must define either a `makeItemView` ' +
             'method or an `itemViewConstructor` property.');
    }
    view.$el.data('cid', item.cid);
    return view;
  },
  _getItemsEl: function () {
    if (this.hasOwnProperty('$itemsEl')) {
      return this.$itemsEl;
    } else if (this.hasOwnProperty('itemsEl')) {
      return this.$(this.itemsEl);
    } else {
      return this.$el;
    }
  },
  renderItems: function (update) {
    var $items = this._getItemsEl()
      , views = this._itemViews

    if (update) {
      _(views).chain().filter(function(view) {
        var attached = !!view.$el.closest(document.documentElement);
        return attached
      }).forEach(function (view) {
        var idx = _.indexOf(views, view);
        if (idx === 0) {
          view.$el.prependTo($items);
        } else {
          view.$el.insertAfter(views[idx - 1].$el);
        }
      });
    } else {
      $items.append(_.pluck(this._itemViews, 'el'));
    }
  },
  sortItemViews: function () {
    this._itemViews.sort(function (a, b) {
      return a.model.get('ordering') - b.model.get('ordering');
    });
  },
  addItem: function (item) {
    var view = this._makeItemView(item);
    this._itemViews.push(view);
    this.sortItemViews();
    this.renderItems(true);
    if (this.onAddItemView) this.onAddItemView(view);
  },
  removeItem: function (item) {
    this._itemViews = _(this._itemViews).filter(function(view) {
      return view.model !== item;
    });
  },
  initSort: function (opts) {
    var that = this
      , $items = this._getItemsEl()
      , defaultSortOpts

    defaultSortOpts = {
      placeholder: 'sort-placeholder',
      cancel: 'input,textarea,button,select,option,.no-sort,.no-sort *',
      cursor: 'pointer',
      cursorAt: { 'left': 200, 'top': 20 },
      axis: 'y',
      tolerance: 'pointer',
      helper: function (event, item) {
        return $(item).clone().addClass('active').css({
          'max-height': '120px',
          'border': 'none',
          'opacity': 0.75
        });
      },
      start: function (event, ui) {
        $(this).addClass('sort-active');
        ui.item.hide();
        $items.sortable('refreshPositions');
      },
      stop: function () {
        $(this).removeClass('sort-active');
      },
      update: function (event, ui) {
        var cid = ui.item.data('cid')
          , model = cid && that.collection.get(cid)
          , ordering
          , origIdx
          , newIdx

        if (!model || model.isNew()) return;

        ui.item.show();
        origIdx = that.collection.indexOf(model);
        newIdx = ui.item.index();

        if (origIdx === newIdx) return;
        if (newIdx > origIdx) newIdx += 1;

        ordering = that.collection.getIntermediateOrderingValue(newIdx);
        model.set('ordering', Math.floor(ordering));
        model.save();
      }
    }

    $items.sortable(_.extend(defaultSortOpts, opts));
  }
});
