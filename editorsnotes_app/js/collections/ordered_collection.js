"use strict";

var _ = require('underscore-contrib')
  , $ = require('jquery')
  , Backbone = require('../backbone')

function makeorderedSave(origSave) {
  return function (attributes, options) {
    var that = this
      , needsNormalization = this.collection.needsNormalization()
      , normalize = this.collection.normalizeOrderingValues.bind(this.collection)
      , refresh = this.collection.refreshOrdering.bind(this.collection)
      , save = origSave.bind(this, attributes, options)
      , dfd

    if (this.isNew()) {
      dfd = needsNormalization ? normalize() : (new $.Deferred()).resolve();
      dfd.then(function () {
        var idx = that.collection.indexOf(that)
          , ordering = that.collection.getIntermediateOrderingValue(idx, true, true)

        ordering = Math.floor(ordering);
        that.set('ordering', ordering);
      }).then(save).done(refresh);
    } else {
      dfd = save();
      if (needsNormalization) dfd.then(normalize).done(refresh);
    }
  }
}

module.exports = Backbone.Collection.extend({
  orderingAttribute: 'ordering',
  orderNormalizationURL: function () { return _.result(this, 'url') + 'normalize_order/' },
  minOrderingStep: 25,

  initialize: function () {
    var orderAwareModel = this.model.extend({});
    orderAwareModel.prototype.save = makeorderedSave(this.model.prototype.save);
    this.model = orderAwareModel;

    this.comparator = this.orderingAttribute;
  },

  /*
   * 
   */
  add: function (models, options) {
    var orderingStart
      , orderingAttribute = this.orderingAttribute

    options = options || {};
    models = _.isArray(models) ? models : [models];

    if (_.isEmpty(models)) return;

    // Get the starting value for the order.
    orderingStart = this.getIntermediateOrderingValue(
      options.hasOwnProperty('at') ? options.at : this.models.length);

    _.forEach(models, function (model, i) {
      var isModel = model instanceof Backbone.Model
        , ordering = orderingStart + (i / models.length)

      if (isModel && (!model.isNew() || model.get(this.orderingAttribute))) return;
      if (!isModel && (model.hasOwnProperty('id') ||
                       model.hasOwnProperty(this.orderingAttribute))) return;

      // If the model has not explicitly set an ordering and does not yet
      // exist, set it automatically.
      if (isModel) {
        model.set(orderingAttribute, ordering);
      } else {
        model[orderingAttribute] = ordering;
      }
    }, this);

    Backbone.Collection.prototype.add.call(this, models, options);
  },

  normalizeOrderingValues: function () {
    var that = this
      , promise = $.ajax({
          type: 'POST',
          beforeSend: function (xhr) {
            xhr.setRequestHeader('X-CSRFToken', $('input[name="csrfmiddlewaretoken"]').val());
          },
          url: _.result(this, 'orderNormalizationURL'),
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
    var orderingAttribute = this.orderingAttribute;

    this.forEach(function (model, idx) {
      var prev, next, startIdx;

      if (model.isNew()) return;

      prev = this.chain()
        .first(idx)
        .reverse()
        .takeWhile(function (model) { return model.isNew() })
        .value();

      if (prev.length) {
        startIdx = this.getIntermediateOrderingValue(idx, true, true);
        prev.forEach(function (model, i) {
          var ordering = startIdx + (i / prev.length);
          model.set(orderingAttribute, ordering);
        });
      }

      next = this.chain()
        .rest(idx)
        .takeWhile(function (model) { return model.isNew() })
        .value();

      if (next.length) {
        startIdx = this.getIntermediateOrderingValue(idx + 1, true, true);
        next.forEach(function (model, i) {
          var ordering = startIdx + (i / next.length);
          model.set(orderingAttribute, ordering);
        });
      }
    }, this);
    this.sort();
  },

  needsNormalization: function () {
    var curMinOrderingStep = this.getMinOrderingStep();

    if (!_.isFinite(curMinOrderingStep)) {
      return true;
    } else if (curMinOrderingStep < this.minOrderingStep) {
      return true;
    } else {
      return false;
    }
  },

  getMinOrderingStep: function () {
    var orderingAttribute = this.orderingAttribute
      , orderings

    orderings = _.chain(this.models)
      .filter(function (model) { return !model.isNew() })
      .map(function (model) { return parseInt(model.get(orderingAttribute), 10) })
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
      order = prevModel.get(this.orderingAttribute) + 100;
    } else if (!prevModel) {
      order = nextModel.get(this.orderingAttribute) / 2;
    } else {
      order = (nextModel.get(this.orderingAttribute) + prevModel.get(this.orderingAttribute)) / 2;
    }

    return order;
  }
});
