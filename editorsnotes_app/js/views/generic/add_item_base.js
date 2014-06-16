"use strict";

/*
 * Base view for all views adding items in a modal
 *
 * Must create saveItem method
 *
 * options:
 *    height
 *    minHeight
 *    width
 */

var $ = require('../../jquery')

module.exports = {
  events: {
    'ajaxStart': 'showLoader',
    'ajaxStop': 'hideLoader',
    'hidden': 'handleHidden',
    'shown': 'setModalSize',
    'click .btn-save-item': 'saveItem'
  },
  renderModal: function () {
    var that = this
      , template = require('../../templates/add_item_modal.html')
      , widget
      , $loader

    widget = template({ type: that.itemType });

    this.$el.children().wrapAll('<div class="modal-body"></div>');
    this.$el
      .addClass('modal')
      .prepend( $(widget).filter('.modal-header') )
      .append( $(widget).filter('.modal-footer') );

    this.$loader = this.$('.loader-icon');
  },

  showLoader: function () { this.$loader.show() },

  hideLoader: function () { this.$loader.hide() },

  handleHidden: function () {
    if (this.model.isNew()) this.model.destroy();
    this.remove();
  },

  setModalSize: function () {
    var that = this
      , options = this.options || {}
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

    bodyHeight = (modalHeight
      - this.$('.modal-header').innerHeight()
      - this.$('.modal-footer').innerHeight()
      - (function (b) {
          var ptop = parseInt(b.css('padding-top'))
            , pbot = parseInt(b.css('padding-bottom'));
          return ptop + pbot;
        })(this.$('.modal-body'))
      - 2); // border

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

