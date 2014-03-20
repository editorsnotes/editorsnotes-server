"use strict";

var assert = require('assert')
  , _ = require('underscore')

describe('Autocompleter widget', function () {
  var Autocompleter = require('../utils/autocomplete_widget')

  describe('instance', function () {
    var testAutocompleter = new Autocompleter(null, 'egp', 'topics');

    it('should query the correct url', function () {
      assert.equal(testAutocompleter.url, '/api/projects/egp/topics/');
    });

    it('should build a query string from a term', function () {
      var query = testAutocompleter.buildQuery('Alexander Berkman');
      assert.deepEqual(query, { 'q': 'Alexander Berkman' });
    });

    it('should create its own input element when not passed one', function () {
      assert.equal(testAutocompleter.$el.length, 1);
    });

    it('should be able to be enabled', function () {
      var $el = testAutocompleter.$el;
      assert.equal(_.isEmpty($el.data('ui-autocomplete')), false);
      assert.equal($el.prop('placeholder'), 'Begin typing to search for topics.');
    });

    it('should be able to be disabled', function () {
      var testAutocompleter = new Autocompleter(null, 'egp', 'topics');
      testAutocompleter.disable();
      assert.equal(_.isEmpty(testAutocompleter.$el.data('ui-autocomplete')), true);
      assert.equal(testAutocompleter.$el.prop('placeholder'), '');
    });

    it('should be able to be enabled after being disabled', function () {
      var testAutocompleter = new Autocompleter(null, 'egp', 'topics')
        , $el = testAutocompleter.$el;

      testAutocompleter.disable();
      testAutocompleter.enable();
      testAutocompleter.disable();
      testAutocompleter.enable();
      assert.equal(_.isEmpty($el.data('ui-autocomplete')), false);
      assert.equal($el.prop('placeholder'), 'Begin typing to search for topics.');
    });

  });

  describe('should throw an error when its constructor', function () {
    it('is not passed a project', function () {
      assert.throws(
        function () { new Autocompleter() },
        /Must pass project slug/
      );
    });

    it('is passed an invalid model', function () {
      assert.throws(
        function () { new Autocompleter(null, 'blah', 'fakemodel') },
        /Invalid model/
      );
    });

    it('is passed an element other than a text input', function () {
      var el = global.document.createElement('div');
      assert.throws(
        function () { new Autocompleter(el, 'blah', 'notes') },
        /Element must be a text input/
      );
    });
  });

});

describe('Text editor', function () {
  var Editor = require('../utils/text_editor.js')

  it('should fail without being passed an element', function () {
    assert.throws(
      function () { new Editor() },
      /Must pass exactly one element/
    );
  });

  it('should fail when passed a non-visible element', function () {
    var el = global.document.createElement('div');
    assert.throws(
      function () { new Editor(el) },
      /Can't edit text of element that is not visible/
    );
  });

  describe('', function () {
    var sandboxes = []
      , sandbox
      , testEl

    beforeEach(function (done) {
      sandbox = global.document.createElement('div');
      testEl = global.document.createElement('p');

      global.document.body.appendChild(sandbox);
      testEl.innerHTML = 'Test content';
      sandbox.appendChild(testEl);

      sandboxes.push(sandbox);
      done();
    });

    after(function (done) {
      _.forEach(sandboxes, function (sandbox) {
        global.document.body.removeChild(sandbox);
      });
      done();
    });

    it('should allow passing a non-jquery element', function () {
      var editor = new Editor(testEl);
      assert.equal(editor.$el[0], testEl);
    });

    it('should assign a unique ID to its element automatically', function () {
      var editor = new Editor(testEl);
      assert.notStrictEqual(editor.id, undefined);
    });

    it('should create its own textarea', function () {
      var editor = new Editor(testEl);
      assert.equal(editor.$textarea.length, 1);
      assert.equal(editor.$textarea.is('textarea'), true);
    });

    it('should create its own toolbar', function () {
      var editor = new Editor(testEl);
      assert.equal(editor.$toolbar.is('div.wysihtml5-toolbar'), true);
    });

    it('should be able to get its own value', function (done) {
      var editor = new Editor(testEl);
      editor.editor.on('load', function () {
        assert.equal(editor.value(), 'Test content');
        done();
      });
    });

    it('should clean up after itself', function (done) {
      var editor = new Editor(testEl);
      editor.editor.on('load', function () {
        editor.value('<p>new value</p>');
        editor.destroy();
      });

      editor.$el.on('editor:destroyed', function (e, val) {
        assert.equal(val, '<p>new value</p>');
        assert.equal(editor.$el.html(), '<p>new value</p>');
        done();
      });
    });
  });
});
