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

var Backbone = require('../backbone')
  , $ = require('jquery')

module.exports = Backbone.View.extend({
  renderModal: function () {
    var that = this
      , template = require('../templates/add_item_modal')
      , widget
      , $loader

    widget = template({
      type: that.itemType,
      textarea: !!that.textarea
    });

    this.$el.html(widget).addClass('modal');
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
      , $w = $(window)
      , modalHeight
      , bodyHeight
      , modalPosition = {
        'my': 'top+20',
        'at': 'top',
        'of': $w,
        'collision': 'none',
      }

    modalHeight = this.options.height || (function () {
      var windowHeight = $w.height() - 50
        , minHeight = that.options.minHeight || 500

      return windowHeight > minHeight ? windowHeight : minHeight;
    })();

    bodyHeight = modalHeight
      - this.$('.modal-header').innerHeight()
      - this.$('.modal-footer').innerHeight()
      - (function (b) {
          var ptop = parseInt(b.css('padding-top'))
            , pbot = parseInt(b.css('padding-bottom'));
          return ptop + pbot;
        })(this.$('.modal-body'))
      - 2; // border

    this.$el.css({
      position: 'absolute',
      width: this.options.width || 840,
      height: modalHeight
    }).position(modalPosition).position(modalPosition);

    this.$('.modal-body').css({
      'height': bodyHeight,
      'max-height': bodyHeight
    });

  }
});

