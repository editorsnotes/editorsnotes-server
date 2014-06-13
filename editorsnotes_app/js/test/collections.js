"use strict";
var assert = require('assert')
  , sinon = require('sinon')
  , $ = require('jquery')

global.sinon = sinon;
require('sinon-event');
require('sinon-fakexhr');

describe('Ordered collection', function () {
  var Backbone = require('backbone')
    , OrderedCollection = require('../collections/ordered_collection')
    , FakeModel = Backbone.Model.extend({})
    , FakeCollection = OrderedCollection.extend({ model: FakeModel })

  var xhr
    , requests = []

  before(function () {
    $('body').append('<input type="hidden" name="csrfmiddlewaretoken" value="fake" />');
    xhr = sinon.useFakeXMLHttpRequest();
    xhr.onCreate = function (xhr1) {
      requests.push(xhr1);
    }
  });

  it('should automatically set ordering for an empty collection', function () {
    var collection = new FakeCollection([])
      , model = collection.add({});

    assert.equal(model.get('ordering'), 100);
  });

  it('should halve ordering at beginning', function () {
    var collection = new FakeCollection([])
      , model1 = collection.add({})
      , model2 = collection.add({}, { at: 0 })
      , model3 = collection.add({}, { at: 0 })

    assert.equal(model1.get('ordering'), 100);
    assert.equal(model2.get('ordering'), 50);
    assert.equal(model3.get('ordering'), 25);
  });

  it('should allow models to be moved explicitly', function () {
    var collection = new FakeCollection([])
      , model1 = collection.add({ ordering: 50 })
      , model2 = collection.add({ ordering: 100 })
      , model3 = collection.add({ ordering: 200 })
      , model4 = collection.add({ ordering: 1000 });

    collection.move(model3, 0);
    assert.equal(model3.get('ordering'), 25);
    assert.deepEqual(collection.pluck('ordering'), [ 25, 50, 100, 1000 ]);

    collection.move(model1, 2);
    assert.equal(model1.get('ordering'), 550);
    assert.deepEqual(collection.pluck('ordering'), [ 25, 100, 550, 1000 ]);

    collection.move(model1, 3);
    assert.equal(model1.get('ordering'), 1100);
    assert.deepEqual(collection.pluck('ordering'), [ 25, 100, 1000, 1100 ]);
  });

  it('should make a call to the server after an existing model is saved if order normalization is required', function () {
    var collection, model1, model2, req;

    collection = new FakeCollection([]);
    collection.url = '/fake/';

    model1 = collection.add({ id: 1, ordering: 10 });
    model2 = collection.add({ id: 2 });
    model2.save();

    req = requests.pop();
    req.respond(
      200, { 'Content-type': 'application/json' },
      JSON.stringify(model2));

    req = requests.pop();
    assert.equal(req.url, collection.url + 'normalize_order/');
    req.respond(
      200, { 'Content-type': 'application/json' },
      JSON.stringify([{ id: 1, ordering: 333 }, { id: 2, ordering: 666 }]));

    assert.equal(model1.get('ordering'), 333);
    assert.equal(model2.get('ordering'), 666);
  });

  it('should make a normalization call before a new model is save if order normalization is required', function () {
    var collection, model1, model2, req;

    collection = new FakeCollection([]);
    collection.url = '/fake/';
    model1 = collection.add({ id: 1, ordering: 10 });
    model2 = collection.add({}, { at: 0 });

    assert.equal(model2.get('ordering'), 5);

    model2.save();
    req = requests.pop();
    assert.equal(req.url, collection.url + 'normalize_order/');
    req.respond(
      200, { 'Content-type': 'application/json' },
      JSON.stringify([{ id: 1, ordering: 500 }]));

    assert.equal(model1.get('ordering'), 500);
    assert.equal(model2.get('ordering'), 250);

    req = requests.pop();
    req.respond(
      200, { 'Content-type': 'application/json' },
      JSON.stringify(model2));
  });

  after(function () {
    xhr.restore();
  });
});
