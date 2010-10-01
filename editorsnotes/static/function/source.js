Seadragon.Config.proxyUrl = '/proxy?url='
$(document).ready(function() {

  // Initialize tabs.
  $('#tabs').tabs({
    select: function(event, ui) { 
      if (ui.panel.id == 'scans') {
        if ($('a.pushed').click().length == 0) {
          $('a.scan:first').click();
        }
      }
    },
  });

  // Initialize scan viewer.
  var viewer = new Seadragon.Viewer('scan-viewer');
  $('#progressbar').progressbar({ value: 0 });
  $('#progress-notify').position({
    of: $('#scan-viewer'),
    my: 'center center',
    at: 'center center'
  }).hide();

  // Scan processing monitor for progress bar.
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

  // Handle scan button clicks.
  $('a.scan').click(function(event) {
    event.preventDefault();
    $('a.pushed').removeClass('pushed');
    $(this).addClass('pushed');
    viewer.close();
    monitor.init('http://api.zoom.it/v1/content/?url=' + encodeURIComponent(this.href));
    monitor.start();
  });

  // Load first scan.
  $('a.scan:first').click();

  var footnote = {
    width: 800,
    display: null,
    setup: function() {
      $('a.footnote').attr('title', 'Click to read footnote');
      $('a.footnote').click(footnote.show);
    },
    resize: function(event, ui) {
      var title = $('#ui-dialog-title-footnote-display');
      if (ui) {
        if (ui.size.width < footnote.width) {
          title.ellipsis(ui.size.width - 50);
        }
      } else {
        title.ellipsis(footnote.width - 50);
      }
    },
    using: function(position) {
      position.left = ((($(window).width() - $(this).width()) / 2) 
                       + $(window).scrollLeft());
      $(this).css(position);
    },
    close: function() {
      $('a.active-footnote').removeClass('active-footnote');
    },
    show: function(event) {
      event.preventDefault();
      if (! footnote.display) {
        footnote.display = $(document.createElement('div'));
        footnote.display.attr('id', 'footnote-display');
        $(document.body).append(footnote.display);
        footnote.display.dialog({ 
          autoOpen: false, 
          draggable: true,
          resizable: true,
          close: footnote.close
        });
      }
      $('a.active-footnote').removeClass('active-footnote');
      $(this).addClass('active-footnote');
      footnote.display.html($('#note-' + $(this).attr('href').split('/')[2]).html());
      footnote.display.dialog('option', 'title', $(this).text());
      footnote.display.dialog('option', 'width', footnote.width);
      footnote.display.dialog('option', 'position', {
        my: 'top', at: 'bottom', of: $(this), offset: '0 5', collision: 'none', 
        using: footnote.using });
      footnote.display.dialog('open');
      footnote.display.bind('dialogresize', footnote.resize);
      footnote.resize();
    }
  }

  footnote.setup();

});