Seadragon.Config.proxyUrl = '/proxy?url='
$(document).ready(function() {

  var viewer = new Seadragon.Viewer('scan-viewer');
  $('#progressbar').progressbar({ value: 0 });
  $('#progress-notify').position({
    of: $('#scan-viewer'),
    my: 'center center',
    at: 'center center'
  }).hide();

  var monitor = {
    init: function(url) {
      this.stop_polling(this);
      this.url = url;
      $('#progressbar').progressbar('option', 'value', 0);
    },
    start: function() {
      this.check(this);
    },
    check: function(self) {
      $.ajax({
        url: self.url,
        dataType: 'jsonp',
        success: function(data) {
          var o = data.content ? data.content : data;
          if (o.ready && o.dzi) {
            self.stop_polling(self);
            $('#progress-notify').hide();
            viewer.openDzi(o.dzi.url);
          } else if (o.failed) {
            self.abort(self, o.url + ' failed to convert.');
          } else {
            var percent = Math.round(100 * o.progress);
            console.log(o.url + ' is ' + percent + '% done.');
            $('#progress-notify').show();
            $('#progressbar').progressbar('option', 'value', percent);
            if (data.redirectLocation) {
              self.url = data.redirectLocation;
              self.start_polling(self);
            }
          }
        },
        error: function(request, status) {
          self.abort(self, 'HTTP request failed: ' + status);
        }
      });
    },
    start_polling: function(self) {
      if (! self.interval_id) {
        self.interval_id = window.setInterval(
          function() { self.check(self); }, 1000);
      }
    },
    stop_polling: function(self) {
      if (self.interval_id) {
        window.clearInterval(self.interval_id);
      }
      self.interval_id = null;
    },
    abort: function(self, message) {
      self.stop_polling(self);
      console.log(message);
      $('#progress-message').text('Oops! Something broke. Please reload the page.').css('color', 'red');
    }
  };

  $('a.scan').click(function(event) {
    event.preventDefault();
    $('a.pushed').removeClass('pushed');
    $(this).addClass('pushed');
    viewer.close();
    monitor.init('http://api.zoom.it/v1/content/?url=' + encodeURIComponent(this.href));
    monitor.start();
  });

  $('a.scan:first').click();
});