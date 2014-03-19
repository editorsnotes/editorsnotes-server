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
