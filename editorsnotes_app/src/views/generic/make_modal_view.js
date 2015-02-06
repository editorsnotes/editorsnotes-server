"use strict";

/*
 * Function that returns a modal editing view for topics, notes, or documents.
 *
 * options:
 *    height
 *    minHeight
 *    width
 */

var $ = require('../../jquery')
  , Cocktail = require('backbone.cocktail')
  , AddItemMixin
  , viewsByType = {
    'topic': require('../topic'),
    'document': require('../document'),
    'note': require('../note')
  }

module.exports = function (type) {
  var View = viewsByType[type];

  if (!View) throw new Error('Cannot render modal for type: ' + type);

  return Cocktail.mixin(View.extend({}), AddItemMixin, { itemType: type });
}

AddItemMixin = {
  events: {
    'ajaxStart': 'showLoader',
    'ajaxStop': 'hideLoader',
    'hidden': 'handleHidden',
    'shown': 'setModalSize',
    'click .btn-save-item': 'saveItem'
  },

  initialize: function () {
    this.$('.save-row').remove();
  },

  render: function () {
    var that = this
      , template = require('../../templates/add_item_modal.html')
      , widget

    debugger;

    widget = template({ type: that.itemType });

    this.$el.children().wrapAll('<div class="modal-body"></div>');
    this.$el
      .addClass('modal')
      .prepend( $(widget).filter('.modal-header') )
      .append( $(widget).filter('.modal-footer') );

    this.$loader = this.$('.loader-icon');
  },

  saveItem: function (e) {
    e.preventDefault();
    this.model.save().then(this.$el.modal.bind(this.$el, 'hide'));
  },

  showLoader: function () { this.$loader.show() },

  hideLoader: function () { this.$loader.hide() },

  handleHidden: function () {
    if (this.model.isNew()) this.model.destroy();
    this.remove();
  },

  setModalSize: function () {
    var options = this.options || {}
      , $w = $(window)
      , modalHeight
      , bodyHeight
      , modalPosition = {
        'my': 'top+20',
        'at': 'top',
        'of': $w,
        'collision': 'none',
      }

    modalHeight = options.height || (function () {
      var windowHeight = $w.height() - 50
        , minHeight = options.minHeight || 500

      return windowHeight > minHeight ? windowHeight : minHeight;
    })();

    bodyHeight = (modalHeight -
      this.$('.modal-header').innerHeight() -
      this.$('.modal-footer').innerHeight() -
      (function (b) {
          var ptop = parseInt(b.css('padding-top'))
            , pbot = parseInt(b.css('padding-bottom'));
          return ptop + pbot;
        })(this.$('.modal-body')) - 2); // Subtract 2 for border

    this.$el.css({
      position: 'absolute',
      width: options.width || 840,
      height: modalHeight
    }).position(modalPosition).position(modalPosition);

    this.$('.modal-body').css({
      'height': bodyHeight,
      'max-height': bodyHeight
    });

  }
}

