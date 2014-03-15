"use strict";

var assert = require('assert');

describe('Note', function () {

  var Note = require('../models/note')

  describe('model', function () {
    var Project = require('../models/project')
      , dummyProject = new Project({ slug: 'emma' })

    it('should throw an error without being passed a project', function () {
      assert.throws(function () { new Note() }, /project/);
    });

    it('should work fine when passed no attrs with a project', function () {
       var note = new Note({}, { project: dummyProject });
       assert.equal(note.project, dummyProject);
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

});
