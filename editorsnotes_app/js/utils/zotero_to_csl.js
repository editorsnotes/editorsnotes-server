"use strict";

var _ = require('underscore')
  , fs = require('fs')
  , z2csl = fs.readFileSync(__dirname + '/../lib/typeMap.xml', 'utf8')
  , parser = new global.DOMParser()
  , doc = parser.parseFromString(z2csl, 'application/xml');

function getTypeMap(itemType) {
  return doc.querySelector('typeMap[zType="' + itemType + '"]');
}

function getCslField(zoteroKey, itemType) {
  var cacheKey = '' + zoteroKey + itemType
    , field
    , lookup
    , map

  if (!getCslField.cache[cacheKey]) {
    field = getTypeMap(itemType).querySelector('[value="' + zoteroKey + '"]');
    lookup = 'map[zField="' + (field.getAttribute('baseField') || zoteroKey) + '"]';
    map = doc.querySelector('cslFieldMap ' + lookup + ', cslCreatorMap ' + lookup);
    getCslField.cache[cacheKey] = map.getAttribute('cslField');
  }

  return getCslField.cache[cacheKey];
}
getCslField.cache = {};

module.exports = function (zoteroObject) {
  var cslObject = {}
    , itemType = zoteroObject.itemType

  cslObject.type = getTypeMap(itemType).getAttribute('cslType');

  _.forEach(zoteroObject, function (val, key) {
    if (!val.length) return;
    switch (key) {
      case 'itemType':
      case 'tags':
        // Not used to generate a citation
        break;
      case 'creators':
        _.forEach(val, function (creator) {
          var creatorObject = {}
            , cslCreatorKey = getCslField(creator.creatorType, itemType)

          if (!(creator.firstName || creator.lastName || creator.name)) {
            return;
          }
          if (!cslObject[cslCreatorKey]) {
            cslObject[cslCreatorKey] = [];
          }
          if (creator.firstName || creator.lastName) {
            creatorObject.given = creator.firstName;
            creatorObject.family = creator.lastName;
          }
          cslObject[cslCreatorKey].push(creatorObject);
        });
        break;
      case 'date':
        cslObject.issued = { 'raw': val };
        break;
      default:
        cslObject[getCslField(key, zoteroObject.itemType)] = val;
        break;
    }
  });

  return cslObject;
}
