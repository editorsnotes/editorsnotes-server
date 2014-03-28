"use strict";

var assert = require('assert')
  , Backbone = require('../backbone')
  , Cocktail = require('backbone.cocktail')

describe('Project-specific base model', function () {
  var ProjectSpecificMixin = require('../models/project_specific_mixin')
    , Project = require('../models/project')
    , ProjectSpecificModel = Backbone.Model.extend({
      constructor: function () {
        ProjectSpecificMixin.constructor.apply(this, arguments);
        Backbone.Model.apply(this, arguments);
      }
    })

  it('should throw an error without being passed a project', function () {
    assert.throws(
      function () { new ProjectSpecificModel() }, 
      /Must pass a project/
    );
  });

  it('should allow a project passed from a collection', function () {
    var CollectionWithProject = Backbone.Collection.extend({})
      , c = new CollectionWithProject({})
      , testinstance

    c.project = new Project({ 'slug': 'egp' });
    testinstance = new ProjectSpecificModel({}, { collection: c });
    assert.equal(testinstance.project, c.project);
  });

  it('should allow a project passed from options', function () {
    var testproject = new Project({ 'slug': 'egp' })
      , testinstance

    testinstance = new ProjectSpecificModel({}, { project: testproject });
    assert.equal(testinstance.project.get('slug'), 'egp');
  });

  it('should allow a project passed in attributes', function () {
    var testinstance = new ProjectSpecificModel({
      'name': 'nothing in particular',
      'project': {
        'name': 'Emma Goldman Papers',
        'url': 'http://example.com/api/projects/egp/'
      }
    });

    assert.equal(testinstance.project.get('slug'), 'egp')
  });
  
  it('should throw an error if passed two different projects', function () {
    var testproject = new Project({ 'slug': 'egp' })
      , data = { 'project': { 'name': 'whatever', 'url': 'http://example.com/api/projects/not_egp/' }}

    assert.throws(
      function () { new ProjectSpecificModel(data, { project: testproject }) },
      /Two different projects passed/
    );
  });
});


describe('Related topics mixin', function () {
  var Topic = require('../models/topic')
    , Project = require('../models/project')
    , RelatedTopicsMixin = require('../models/related_topics_mixin')
    , ProjectSpecificMixin = require('../models/project_specific_mixin')
    , TestModel = Backbone.Model.extend({
      constructor: function () {
        ProjectSpecificMixin.constructor.apply(this, arguments);
        RelatedTopicsMixin.constructor.apply(this, arguments);
        Backbone.Model.apply(this, arguments);
      }
    })
    , dummyProject = new Project({ slug: 'emma' })

  Cocktail.mixin(TestModel, RelatedTopicsMixin.mixin);

  it('Should set an object\'s related_topics attribute', function () {
    var obj = new TestModel({}, { project: dummyProject });
    obj.relatedTopics.add({ 'preferred_name': 'Emma Goldman' });
    assert.equal(obj.get('related_topics').length, 1);
    assert.equal(obj.get('related_topics')[0], 'Emma Goldman');
  });

  it('Should not update a related_topics attribute for duplicate topics', function () {
    var obj = new TestModel({}, { project: dummyProject });
    obj.relatedTopics.add({ preferred_name: 'Alexander Berkman', id: 123 });
    obj.relatedTopics.add({ preferred_name: 'Alexander Berkman', id: 123 });
    assert.equal(obj.get('related_topics').length, 1);
  });

});


describe('Note', function () {
  var Note = require('../models/note')
    , Project = require('../models/project')
    , dummyProject = new Project({ slug: 'emma' })

  it('should throw an error without being passed a project', function () {
    assert.throws(
      function () { new Note() }, 
      /Must pass a project/
    );
  });

  it('should have an absolute url', function () {
    var note = new Note({}, { project: dummyProject });
    assert.equal(note.url(), '/api/projects/emma/notes/');
  });

  it('should have an absolute url with ID', function () {
    var note = new Note({id: 12}, { project: dummyProject });
    assert.equal(note.url(), '/api/projects/emma/notes/12/');
  });

  it('should have a default status of open', function () {
    var note = new Note({}, { project: dummyProject });
    assert.equal(note.get('status'), 'open');
  });
});


describe('Topic', function () {
  var Topic = require('../models/topic')
    , Project = require('../models/project')
    , dummyProject = new Project({ slug: 'emma' })

  it('should have an absolute url as a new item', function () {
    var topic = new Topic({}, { project: dummyProject });
    assert.equal(topic.url(), '/api/projects/emma/topics/');
  });

  it('should derive its url from its topic node id', function () {
    var topic = new Topic({ 'id': 99, 'topic_node_id': 88 }, {
      parse: true,
      project: dummyProject
    });

    assert.equal(topic.url(), '/api/projects/emma/topics/88/');
  });
});


describe('Document', function () {
  var Document = require('../models/document')
    , Project = require('../models/project')
    , dummyProject = new Project({ slug: 'emma' })

  it('should have the right base URL', function () {
    var dokument = new Document({}, { project: dummyProject });
    assert.equal(dokument.url(), '/api/projects/emma/documents/');
  });
});
