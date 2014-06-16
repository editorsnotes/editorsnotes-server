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

    $loader = this.$('.loader-icon');

    this.$el
      .on('ajaxStart', function () { $loader.show(); })
      .on('ajaxStop', function () { $loader.hide(); })
      .on('hidden', that.remove.bind(that))
      .on('shown', that.setModalSize.bind(that))
      .on('click', '.btn-save-item', that.saveItem.bind(that));
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

