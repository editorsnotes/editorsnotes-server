"use strict";

var leaflet = require('leaflet')
  , Backbone = require('../../backbone')

module.exports = Backbone.View.extend({
  events: {
    'click #scan-list a.scan': 'handleClick'
  },
  initialize: function () {
    this.render();
    this.$viewer = this.$('#scan-viewer2');
    this.$viewer.css({ width: '100%', height: 700 });
    this.initMap();

    setTimeout(function () {
      this.$('#scan-list a.scan').first().trigger('click');
    }, 0);
  },
  render: function () {
    var template = require('./templates/scans.html');
    this.$el.html(template({ scans: this.model.scans.toJSON() }));
  },
  initMap: function () {
    this.map = leaflet.map('scan-viewer2', {
      minZoom: 1,
      maxZoom: 8,
      center: [0, 0],
      zoom: 2,
      crs: leaflet.CRS.Simple,
      attributionControl: false
    });
  },
  handleClick: function (e) {
    if (!e.ctrlKey && !e.shiftKey) {
      e.preventDefault();
      this.renderScan(e.target.href, e.target.dataset.height, e.target.dataset.width);
    }
  },
  renderScan: function (url, height, width) {
    var sw = this.map.unproject([0, height], this.map.getMaxZoom() - 3)
      , ne = this.map.unproject([width, 0], this.map.getMaxZoom() - 3)
      , bounds = new leaflet.LatLngBounds(sw, ne);

    if (this.currentImage) {
      this.map.removeLayer(this.currentImage);
    }

    this.currentImage = leaflet.imageOverlay(url, bounds);
    this.currentImage.addTo(this.map);
    this.map.setMaxBounds(bounds);
    this.map.fitBounds(bounds, { animate: false });
    if (this.map.getZoom() > 5) {
      this.map.setZoom(5, { animate: false });
    }
  }
});
