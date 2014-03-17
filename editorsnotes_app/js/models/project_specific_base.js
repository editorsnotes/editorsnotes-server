"use strict";

var Backbone = require('../backbone')
  , _ = require('underscore')
  , Project = require('./project')

/*
 * Base model for objects which need to have a project set.
 *
 * Looks for attribute, collection, and explicit passing in options. Will raise
 * an error if no project is found, or if different projects are found.
 */
module.exports = Backbone.Model.extend({
  constructor: function (attributes, options) {
    var candidates, results, slug;

    candidates = {
      options: options && options.project,
      collection: options && options.collection && options.collection.project,
      attributes: attributes && attributes.project
    }

    if (candidates.attributes) {
      slug = candidates.attributes.url.match(/[^\/]+/g).slice(-1);
      candidates.attributes = new Project({
        name: candidates.attributes.name,
        slug: slug
      });
    }

    results = _.chain(candidates).filter(function (p) { return p instanceof Project });

    if (!results.value().length) {
      throw new Error('Must pass a project object, either in options, collection, or attributes.');
    }


    if (results.map(function (p) { return p.get('slug') }).uniq().value().length > 1) {
      throw new Error('Two different projects passed. Not possible.')
    }

    // Take the first result
    this.project = results.first().value();

    Backbone.Model.apply(this, arguments);
  }
});
