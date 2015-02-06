"use strict";

var fs = require('fs')
  , locales = {}

locales['en-US'] = fs.readFileSync(__dirname + '/../lib/citeproc-js/locales/locales-en-US.xml', 'utf8');

module.exports = locales;
