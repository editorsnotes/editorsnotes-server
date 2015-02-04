"use strict";

var assert = require('assert')
  , sinon = require('sinon')

global.sinon = sinon;
require('sinon-event');
require('sinon-fakexhr');

describe('Zotero editing view', function () {
  var ZoteroItemView = require('../views/edit_zotero')
    , requests = []
    , testData
    , xhr

  testData = {
    itemType: 'book',
    title: 'Living My Life',
    creators: [{ creatorType: 'author', firstName: 'Emma', lastName: 'Goldman' }],
    date: '1931'
  }

  before(function () {
    xhr = sinon.useFakeXMLHttpRequest();
    xhr.onCreate = function (xhr1) {
      requests.push(xhr1);
    }
  });

  it('should produce the same data that it was asked to render', function (done) {
    var view = new ZoteroItemView({ zoteroData: testData });

    requests.pop().respond(
      200, {"Content-type": "application/json"}, 
      JSON.stringify([{ creatorType: 'author', localized: 'Author' }]));

    view.on('updatedZoteroData', function (data) {
      assert.deepEqual(data, testData);
      done();
    });

    view.$('.zotero-entry').first().trigger('input');
  });

  after(function () {
    xhr.restore();
  });
});
