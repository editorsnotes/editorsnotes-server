"use strict";

module.exports = function (text, length) {
  var l = length || 100;
  return text.length < l ? text : 
    text.substr(0, l/2) + ' ... ' + text.substr(-(l/2));
}
