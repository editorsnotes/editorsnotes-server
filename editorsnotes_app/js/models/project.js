"use strict";

/*
 * As things stand now, items (documents, notes, topics) should be added
 * within a project instance. This eases things in terms of dealing with
 * URLs, although that could be changed in the future.
 */

var Backbone = require('../backbone')
  , DocumentCollection = require('../collections/document')
  , NoteCollection = require('../collections/note')
  , TopicCollection = require('../collections/topic')

module.exports = Backbone.Model.extend({
  initialize: function (attributes, options) {

    // If a slug was not explictly passed to the project instance, try to
    // derive it from the current URL
    var slug = (attributes && attributes.slug) || (function (pathname) {
      var match = pathname.match(/^\/(?:api\/)?projects\/([^\/]+)/)
      return match && match[1];
    })(document.location.pathname);

    // Throw an error if a slug could not be determined. Without that, we
    // can't determine the URL for documents/notes/topics.
    if (!slug) {
      throw new Error('Could not get project without url or argument');
    }
    this.set('slug', slug);

    // Instantiate the collections for documents, notes, and topics.
    this.documents = new DocumentCollection([], { project: this });
    this.notes = new NoteCollection([], { project: this });
    this.topics = new TopicCollection([], { project: this });

  },

  url: function () { return '/api/projects/' + this.get('slug') + '/'; }

});
