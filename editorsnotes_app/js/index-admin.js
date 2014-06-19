"use strict";

var Backbone = require('./backbone')
  , $ = require('./jquery')
  , Editor = require('./utils/text_editor')
  , Project = require('./models/project')
  , AdminRouter

$(document).ready(function () {
  var admin = new AdminRouter();

  var feedbackHtml = (
    '<div class="feedback-prompt">' +
      '<span class="feedback-label">Feedback</span>' +
      '<i class="icon-plus"></i>' +
    '</div>');

  var $feedback = $(feedbackHtml)
    .appendTo('body')
    .on('click', function () {
      var FeedbackView = require('./views/feedback')
        , view = new FeedbackView({ purpose: 'Feedback' });

      view.$el.on('shown', function () { $feedback.hide() });
      view.$el.on('hidden', function () { $feedback.show() });
    });

  // pushState doesn't actually matter here because we just use normal anchor
  // tags for page transitions (ie this is not a single page app (..yet?))
  Backbone.history.start({ pushState: true });
});

AdminRouter = Backbone.Router.extend({
  routes: {
    'projects/:project/documents/add/': 'editDocument',
    'projects/:project/documents/:id/edit/': 'editDocument',
    'projects/:project/notes/add/': 'editNote',
    'projects/:project/notes/:id/edit/': 'editNote',
    'projects/:project/topics/add/': 'editTopic',
    'projects/:project/topics/:id/edit/': 'editTopic'
  },

  _view: null,

  changeView: function (view) {
    if (this._view) this._view.remove();
    this._view = view;
  },

  makeModelInstance: function (Model, projectSlug, id) {
    var instance
      , project

    if (global.EditorsNotes.bootstrap) { 
      instance = new Model(global.EditorsNotes.bootstrap, { parse: true });
    } else if (id) {
      // TODO (or don't)
    } else {
      // New item
      project = new Project({ slug: projectSlug });
      instance = new Model({}, { project: project });
    }

    return instance;
  },

  makeModelView: function (Model, View, projectSlug, id) {
    var instance = this.makeModelInstance(Model, projectSlug, id);
    return new View({ model: instance, el: '#main' });
  },

  editDocument: function (project, id) {
    var Document = require('./models/document')
      , DocumentView = require('./views/document')
      , view

    view = this.makeModelView(Document, DocumentView, project, id);
    this.changeView(view);
  },

  editNote: function (project, id) {
    var Note = require('./models/note')
      , NoteView = require('./views/note')
      , view

    view = this.makeModelView(Note, NoteView, project, id);
    this.changeView(view);
  },

  editTopic: function (project, id) {
    var Topic = require('./models/topic')
      , TopicView = require('./views/topic')
      , view

    view = this.makeModelView(Topic, TopicView, project, id);
    this.changeView(view);
  }
  
});

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

$(document).ready(function () {
  // Initialize text editors
  $('textarea.xhtml-textarea:visible').each(function (idx, textarea) {
    $(textarea).editText();
  });
});
