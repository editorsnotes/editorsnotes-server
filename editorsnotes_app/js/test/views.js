"use strict";

var assert= require('assert')

describe('Zotero editing view', function () {
  var ZoteroItemView = require('../views/edit_zotero')
    , testData

  testData = {
    itemType: 'book',
    title: 'Living My Life',
    creators: [{ creatorType: 'author', firstName: 'Emma', lastName: 'Goldman' }],
    date: '1931'
  }

  it('should produce the same data that it was asked to render', function (done) {
    var view = new ZoteroItemView({ zoteroData: testData });

    view.on('updatedZoteroData', function (data) {
      assert.deepEqual(data, testData);
      done();
    });

    view.$('.zotero-entry').first().trigger('input');
  });

});
