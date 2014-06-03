"use strict";

var _ = require('underscore-contrib')
  , $ = require('jquery')
  , Backbone = require('../backbone')
  , NoteSection = require('../models/note_section')
  , MINIMUM_STEP = 25

NoteSection.prototype.save = function (attributes, options) {
  var that = this
    , minStep = this.collection.getMinOrderingStep()
    , save = Backbone.Model.prototype.save.bind(this, attributes, options)
    , normalize = this.collection.normalizeOrderingValues.bind(this.collection)
    , refresh = this.collection.refreshOrdering.bind(this.collection)
    , dfd

  if (this.isNew()) {
    dfd = minStep < MINIMUM_STEP ? normalize() : (new $.Deferred()).resolve();
    dfd.then(function () {
      var idx = that.collection.indexOf(that)
        , ordering = that.collection.getIntermediateOrderingValue(idx, true, true)

      ordering = Math.floor(ordering);
      that.set('ordering', ordering);
    }).then(save).done(refresh);
  } else {
    dfd = save();
    if (minStep < MINIMUM_STEP) {
      dfd.then(normalize).done(refresh);
    }
  }

  return dfd.promise();
}

module.exports = Backbone.Collection.extend({
  model: NoteSection,
  comparator: 'ordering',

  initialize: function (models, options) {
    this.project = options.project;
  },

  add: function (models, options) {
    var orderingStart;

    options = options || {};
    models = _.isArray(models) ? models : [models];

    if (_.isEmpty(models)) return;

    // Get the starting value for the order.
    orderingStart = this.getIntermediateOrderingValue(
      options.hasOwnProperty('at') ? options.at : this.models.length);

    _.forEach(models, function (model, i) {
      var isModel = model instanceof Backbone.Model
        , ordering = orderingStart + (i / models.length)

      if (isModel && (model.get('id') || model.get('ordering'))) return;
      if (!isModel && (model.hasOwnProperty('id') || model.hasOwnProperty('ordering'))) return;

      // If the model has not explicitly set an ordering and does not yet
      // exist, set it automatically.
      if (isModel) {
        model.set('ordering', ordering);
      } else {
        model.ordering = ordering;
      }
    });

    Backbone.Collection.prototype.add.call(this, models, options);
  },

  parse: function (response) {
    return response.sections;
  },

  normalizeOrderingValues: function () {
    var that = this
      , promise = $.ajax({
          type: 'POST',
          beforeSend: function (xhr) {
            xhr.setRequestHeader('X-CSRFToken', $('input[name="csrfmiddlewaretoken"]').val());
          },
          url: this.url + 'normalize_section_order/',
          data: {}
        });

    promise.done(function (data) {
      that.set(data, { add: false, remove: false, sort: false });
      that.refreshOrdering();
    });

    return promise;
  },

  // Assumes that the sections are in order, and changes `ordering` values
  // accordingly. This is especially important for unsaved sections that cannot
  // be given values with the `normalizeOrderingValues` method.
  refreshOrdering: function () {
    this.forEach(function (section, idx) {
      var prev, next, startIdx;

      if (section.isNew()) return;

      prev = this.chain()
        .first(idx)
        .reverse()
        .takeWhile(function (section) { return section.isNew() })
        .value();

      if (prev.length) {
        startIdx = this.getIntermediateOrderingValue(idx, true, true);
        prev.forEach(function (section, i) {
          var ordering = startIdx + (i / prev.length);
          section.set('ordering', ordering);
        });
      }

      next = this.chain()
        .rest(idx)
        .takeWhile(function (section) { return section.isNew() })
        .value();

      if (next.length) {
        startIdx = this.getIntermediateOrderingValue(idx + 1, true, true);
        next.forEach(function (section, i) {
          var ordering = startIdx + (i / next.length);
          section.set('ordering', ordering);
        });
      }
    }, this);
    this.sort();
  },

  getMinOrderingStep: function () {
    var orderings;

    orderings = _.chain(this.models)
      .filter(function (model) { return !model.isNew() })
      .map(function (model) { return parseInt(model.get('ordering'), 10) })
      .sort(function (a, b) { return a - b })
      .value();

    if (_.any(orderings, _.isNaN)) return 0;

    return _.chain(orderings)
      .map(function (n, i, arr) { return arr[i + 1] - n; })
      .filter(Boolean)
      .min()
      .value();
  },

  getIntermediateOrderingValue: function (idx, skipIdx, skipNew) {
    var prevModel, nextModel, order;

    idx = idx || 0;

    prevModel = idx <= 0 ? null : this.at(idx - 1);
    if (prevModel && skipNew) {
      prevModel = this.chain()
        .first(idx)
        .reverse()
        .filter(function (model) { return !model.isNew() })
        .first()
        .value();
    }

    nextModel = idx >= this.length ? null : this.at(idx + (skipIdx ? 1 : 0));
    if (nextModel && skipNew) {
      nextModel = this.chain()
        .rest(idx)
        .filter(function (model) { return !model.isNew() })
        .first()
        .value();
    }

    if (!prevModel && !nextModel) {
      order = 100;
    } else if (!nextModel) {
      order = prevModel.get('ordering') + 100;
    } else if (!prevModel) {
      order = nextModel.get('ordering') / 2;
    } else {
      order = (nextModel.get('ordering') + prevModel.get('ordering')) / 2;
    }

    return order;
  }
});

