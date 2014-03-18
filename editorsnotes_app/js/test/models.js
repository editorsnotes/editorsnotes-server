"use strict";

var assert = require('assert')
  , Backbone = require('../backbone')

describe('Project-specific base model', function () {
  var ProjectSpecificBaseModel = require('../models/project_specific_base')
    , Project = require('../models/project')

  it('should throw an error without being passed a project', function () {
    assert.throws(
      function () { new ProjectSpecificBaseModel() }, 
      /Must pass a project/
    );
  });

  it('should allow a project passed from a collection', function () {
    var CollectionWithProject = Backbone.Collection.extend({})
      , c = new CollectionWithProject({})
      , testinstance

    c.project = new Project({ 'slug': 'egp' });
    testinstance = new ProjectSpecificBaseModel({}, { collection: c });
    assert.equal(testinstance.project, c.project);
  });

  it('should allow a project passed from options', function () {
    var testproject = new Project({ 'slug': 'egp' })
      , testinstance

    testinstance = new ProjectSpecificBaseModel({}, { project: testproject });
  });

  it('should allow a project passed in attributes', function () {
    var testinstance = new ProjectSpecificBaseModel({
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
      function () { new ProjectSpecificBaseModel(data, { project: testproject }) },
      /Two different projects passed/
    );
  });
});


describe('Related topics mixin', function () {
  var RelatedTopicsMixin = require('../models/related_topics_mixin')
    , ProjectSpecificBaseModel = require('../models/project_specific_base')
    , TestModel = ProjectSpecificBaseModel.extend(RelatedTopicsMixin)
    , Project = require('../models/project')
    , dummyProject = new Project({ slug: 'emma' })

  it('Should set an object\'s related_topics attribute', function () {
    var obj = new TestModel({}, { project: dummyProject });
    obj.getRelatedTopicList().add({ 'preferred_name': 'Emma Goldman' });
    assert.equal(obj.get('related_topics').length, 1);
    assert.equal(obj.get('related_topics')[0], 'Emma Goldman');
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

  it('should assume if only passed an id that it is the topic_node_id', function () {
    var topic = new Topic({ 'id': 123 }, {
      parse: true,
      project: dummyProject
    });

    assert.equal(topic.get('topic_node_id'), 123);
  });

  it('should create an id attribute based on both project and topic_node_id', function () {
    var topic = new Topic({ 'topic_node_id': 123 }, {
      parse: true,
      project: dummyProject
    });

    assert.equal(topic.isNew(), false);
    assert.equal(topic.id, dummyProject.get('slug') + '123')
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
