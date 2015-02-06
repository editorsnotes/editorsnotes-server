"use strict";

var _ = require('underscore')
  , wysihtml5 = require('wysihtml5')
  , toolbarTemplate = require('./templates/wysihtml5_toolbar.html')
  , defaults
  , wysihtml5Opts

defaults = {
    toolbarType: 'full',
    className: '',
    height: null,
    minHeight: 200,
    idPrefix: 'texteditor_id_auto',
    container: '',
    initialValue: null,
    afterInit: null,
    destroy: null
}

wysihtml5Opts = {
  parserRules: require('./wysihtml5_parser_rules_min'),
  stylesheets: ['/static/function/lib/wysihtml5/wysihtml5-stylesheet.css'],
  useLineBreaks: false
}

function Editor( $el, opts ){
  var that = this
    , $ = require('../jquery')

  $el = $el instanceof $ ? $el : $($el);

  if ($el.length !== 1 || $el[0].nodeType !== window.document.ELEMENT_NODE) {
    throw new Error('Must pass exactly one element.')
  }

  if (!$el.is(':visible')) {
    throw new Error('Can\'t edit text of element that is not visible.');
  }

  this.options = _.extend({}, defaults, opts);

  this.$el = $el;
  this.isTextarea = this.$el.is('textarea');
  this.id = (this.isTextarea && this.$el.attr('id')) || _.uniqueId(that.options.idPrefix);
  this.$toolbar = $(toolbarTemplate({ id: that.id + '-toolbar', type: that.options.toolbarType }));

  this.height = this.options.height || (function (h) {
    return h < that.options.minHeight ? that.options.minHeight : h;
  })(this.$el.innerHeight());

  this.$container = this.options.container ?
    this.$el.closest( this.options.container ) :
    this.$el.parent();

  this.init();

  return this;
}

Editor.prototype.init = function () {
  var that = this
    , $ = require('../jquery')
    , content

  if ('initialValue' in this.options && this.options.initialValue !== null) {
    content = _.result(this.options, 'initialValue');
  } else {
    content = this.isTextarea ? this.$el.val() : this.$el.html();
  }

  this.$textarea = this.isTextarea ?
    this.$el : $('<textarea>').appendTo(this.$container)

  this.$container.css('min-height', that.height + 8);

  this.$textarea
    .attr('id', that.id)
    .css({
      opacity: 0,
      height: that.height,
      width: '99%'
    })
    .val(content)

  if (!this.isTextarea) this.$el.hide();

  this.$toolbar.insertBefore(that.$textarea);
  this.editor = new wysihtml5.Editor(that.id, _.extend({
    toolbar: that.$toolbar.attr('id')
  }, wysihtml5Opts));

  this.editor.on('load', function () {
    that.$container.css('min-height', '')
  });

  this.editor.on('change', function () {
    that.$el.trigger('editor:change', that.editor.getValue());
  });
  
  this.editor.on('input', function () {
    that.$el.trigger('editor:input', that.editor.getValue());
  });

  if ( typeof(this.options.afterInit) === 'function' ) {
    this.options.afterInit.call( that );
  }

  return this.$el;
}

Editor.prototype.destroy = function () {
  var that = this
    , finalVal = this.editor.getValue()
    , toRemove = [
      'iframe.wysihtml5-sandbox',
      'input[name="_wysihtml5_mode"]',
    ]

  this.$container.find(toRemove.join(',')).remove();

  if (this.isTextarea) {
    this.$el.val(finalVal);
  } else {
    this.$textarea.remove();
  }

  this.$toolbar.remove();

  if ( typeof(this.options.destroy) === 'function' ) {
    this.options.destroy.call( that.$el, finalVal );
  }

  this.$el
    .html(finalVal)
    .show()
    .removeData('editor')
    .trigger('editor:destroyed', finalVal); 

}

Editor.prototype.value = function (val) {
  if (!val) {
    return this.editor.getValue()
  } else {
    this.editor.setValue(val);
  }
}

module.exports = Editor;
