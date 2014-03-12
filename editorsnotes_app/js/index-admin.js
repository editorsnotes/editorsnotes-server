"use strict";

var EditorsNotes = window.EditorsNotes
  , $ = require('jquery')
  , Editor = require('./utils/text_editor')

EditorsNotes.Models = {
  Project: require('./models/project')
}
EditorsNotes.Views = {
  Note: require('./views/note')
}

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
