"use strict";

var Backbone = require('../backbone')
  , _ = require('underscore')

module.exports = Backbone.View.extend({
  events: {
    'click .delete-scan': 'handleDeleteClick',
    'click .move-scan': 'handleMoveClick',
    'dragover #scan-drop': function (e) { e.preventDefault(); e.stopPropagation(); },
    'dragenter #scan-drop': 'handleDragenter',
    'dragleave #scan-drop': 'handleDragleave',
    'drop #scan-drop.drop-ready': 'handleDrop'
  },
  className: 'scan-container',
  initialize: function () {
    this.render();
    if (this.collection.needsNormalization()) {
      this.collection.normalizeOrderingValues();
    }
    this.listenTo(this.collection, 'add remove sort', this.render);
  },
  render: function () {
    var that = this
      , template = require('../templates/scans.html')

    this.$el.html( template({ scans: that.collection }) );
    this.$dropTarget = this.$('#scan-drop');
    this.refreshScanButtons();
  },
  handleDeleteClick: function (e) {
    e.preventDefault();
    var cid = e.target.dataset.scan
      , scan = this.collection.get(cid)

    scan.destroy();
    this.render();
  },
  handleMoveClick: function (e) {
    var scan = this.collection.get(e.target.dataset.scan)
      , direction = parseInt(e.target.dataset.direction, 10);

    this.collection.move(scan, this.collection.indexOf(scan) + direction);
  },
  refreshScanButtons: function () {
    var $moveBtns = this.$('.move-scan').prop('disabled', false);
    $moveBtns.first().prop('disabled', 'true');
    $moveBtns.last().prop('disabled', 'true');
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
