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

describe('Note', function () {
  var Note = require('../models/note')
    , Project = require('../models/project')
    , dummyProject = new Project({ slug: 'emma' })

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
