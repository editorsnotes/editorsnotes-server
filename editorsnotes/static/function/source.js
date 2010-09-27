Seadragon.Config.proxyUrl = '/proxy?url='
$(document).ready(function () {
  var viewer = new Seadragon.Viewer('scan-viewer');
  $('a.scan').click(function(event) {
    event.preventDefault();
    console.log(this.href);
    $.ajax({
      url: 'http://api.zoom.it/v1/content/?url=' + encodeURIComponent(this.href),
      dataType: 'jsonp',
      success: function(data) {
        var o = data.content;
        if (o.ready && o.dzi) {
          viewer.openDzi(o.dzi.url);
        } else if (o.failed) {
          console.log(o.url + ' failed to convert.');
        } else {
          console.log(o.url + ' is ' + Math.round(100 + o.progress) + '% done.');
        }
      },
      error: function(request, status) {
        console.log('zoom.it of ' + this.href + ' failed: ' + status);
      }
    });
  });
  $('a.scan:first').click();
});