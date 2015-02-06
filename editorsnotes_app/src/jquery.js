"use strict";

var $ = window.jQuery = window.$ = require('jquery')
  , Editor = require('./utils/text_editor')

require('jquery-ui')
require('jquery-ui-touch-punch')
require('jquery-timeago')
require('jquery-bootstrap')

$.fn.editText = function (method) {
  var editor = this.data('editor');

  if (this.length !== 1) $.error('One at a time :(');

  if ( typeof(method) === 'object' || !method  ) {
    if (editor) return this;
    return this.data('editor', new Editor(this, method || {}));
  } else if ( !editor ) {
    $.error('Must initialize editor first.');
  } else if ( Editor.prototype[method] ) {
    return editor[method].apply(editor, Array.prototype.slice.call(arguments, 1));
  } else {
    $.error('No such method: ' + method);
  }
}

module.exports = $;
