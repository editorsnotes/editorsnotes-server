"use strict";

var Backbone = require('../backbone')
  , _ = require('underscore')

module.exports = Backbone.View.extend({
  events: {
    'click .delete-scan': 'handleDeleteClick',
    'dragover #scan-drop': function (e) { e.preventDefault(); e.stopPropagation(); },
    'dragenter #scan-drop': 'handleDragenter',
    'dragleave #scan-drop': 'handleDragleave',
    'drop #scan-drop.drop-ready': 'handleDrop'
  },
  initialize: function () {
    this.render();
  },
  render: function () {
    var that = this
      , template = require('../templates/scans.html')

    this.$el.html( template({ scans: that.collection }) );
    this.$dropTarget = this.$('#scan-drop');
  },
  handleDeleteClick: function (e) {
    e.preventDefault();
    var cid = e.target.dataset.scan
      , scan = this.collection.get(cid)

    scan.destroy();
    this.render();
  },
  getImageFiles: function (fileList) {
    var imageFiles = [];
    for (var i = 0; i < fileList.length; i++) {
      if (fileList[i].type.match('image/')) {
        imageFiles.push(fileList[i]);
      }
    }
    return imageFiles;
  },
  handleDragenter: function (e) {
    e.preventDefault();
    e.stopPropagation();

    var dt = e.originalEvent.dataTransfer;

    if (_.contains(dt.types, 'Files')) {
      this.$dropTarget.addClass('drop-ready').css('background', '#f0f0f0');
    }
  },
  handleDragleave: function () {
    this.$dropTarget.removeClass('drop-ready').css('background', '');
  },
  handleDrop: function (e) {
    e.preventDefault();
    var imageFiles = this.getImageFiles(e.originalEvent.dataTransfer.files);
    this.handleDragleave();

    imageFiles.forEach(function (imageFile) {
      var that = this;
      this.collection
        .add({ image_file: imageFile })
        .save().done(that.render.bind(that));
    }, this);
  }
});
