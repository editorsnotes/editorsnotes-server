"use strict";

var Backbone = require('./backbone')
  , $ = require('./jquery')
  , Project = require('./models/project')
  , AdminRouter

$(document).ready(function () {
  initFeedback();
  initEditors();

  window.EditorsNotes.admin = new AdminRouter();
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

    if (window.EditorsNotes.bootstrap) {
      instance = new Model(window.EditorsNotes.bootstrap, { parse: true });
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
      , DocumentView = require('./admin/document')
      , view

    view = this.makeModelView(Document, DocumentView, project, id);
    this.changeView(view);
  },

  editNote: function (project, id) {
    var Note = require('./models/note')
      , NoteView = require('./admin/note')
      , view

    view = this.makeModelView(Note, NoteView, project, id);
    this.changeView(view);
  },

  editTopic: function (project, id) {
    var Topic = require('./models/topic')
      , TopicView = require('./admin/topic')
      , view

    view = this.makeModelView(Topic, TopicView, project, id);
    this.changeView(view);
  }

});

// Add a button for feedback
function initFeedback() {
  var FeedbackView = require('./admin/widgets/feedback')
    , feedbackHint = new FeedbackView()

  feedbackHint.$el.appendTo('body');
}

// Initialize text editors for textareas with the magic word in the class name
// TODO: remove?
function initEditors() {
  $('textarea.xhtml-textarea:visible').each(function (idx, textarea) {
    $(textarea).editText();
  });
}
