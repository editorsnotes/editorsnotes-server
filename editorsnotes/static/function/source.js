Seadragon.Config.proxyUrl = '/proxy?url='
$(document).ready(function() {

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
            self.abort(self, o.url + ' failed to convert: ' + o.shareUrl);
          } else {
            var percent = Math.round(100 * o.progress);
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

  var footnote = {
    done: false,
    width: 800,
    display: null,
    setup: function() {
      if (footnote.done) { return; }
      footnote.done = true;
      console.log('setting up footnotes');
      var footnotes = $('a.footnote');
      footnotes.attr('title', 'Click to read footnote');
      footnotes.click(footnote.show);
      var markers = $(document.createElement('ul'));
      markers.attr('id', 'footnote-markers').appendTo($('#transcript-content'));
      var i = 1;
      footnotes.each(function() {
        var a = $(this);
        var marker = $(document.createElement('li'));
        marker.appendTo(markers);
        marker.position({
          my: 'center top',
          at: 'left top',
          of: a,
          collision: 'none',
          using: function(position) {
            position.top -= 4;
            position.left = -10;
            $(this).css(position);
          }
        });
        var punc = '';
        if (a[0].nextSibling && a[0].nextSibling.nodeType == 3) { // text node
          var text = $(a[0].nextSibling).text();
          if (text.length > 0 && (text[0] == ',' || text[0] == '.')) {
            punc = text[0];
            $(a[0].nextSibling).replaceWith(
              $(document.createTextNode(text.slice(1))));
          }
        }
        var number = $(document.createElement('span'));
        number.addClass('footnote-number');
        number.html(punc + '<small><sup title="Click to read footnote">' + i + '</sup></small>');
        a.after(number);
        number.hover(function() { a.toggleClass('hover-footnote'); },
                     function() { a.toggleClass('hover-footnote'); } );
        a.hover(function() { number.toggleClass('hover-footnote'); },
                function() { number.toggleClass('hover-footnote'); } );
        number.click(function() { a.click(); });
        a.data('footnote-number', i);
        i += 1;
      });
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
      var link = $(this);
      link.addClass('active-footnote');
      footnote.display.html($('#note-' + link.attr('href').split('/')[2]).html());
      var linktext = link.text();
      if (! linktext.match(/^[A-Z"']/)) {
        linktext = '&hellip; ' + linktext;
      }
      footnote.display.dialog('option', 'title', link.data('footnote-number') + '. ' + linktext);
      footnote.display.dialog('option', 'width', footnote.width);
      footnote.display.dialog('option', 'position', {
        my: 'top', at: 'bottom', of: link, offset: '0 5', collision: 'none', 
        using: footnote.using });
      footnote.display.dialog('open');
      footnote.display.bind('dialogresize', footnote.resize);
      footnote.resize();
    }
  }

  // Initialize tabs.
  $('#tabs').tabs({
    show: function(event, ui) { 
      console.log(ui);
      if (ui.panel.id == 'scans') {
        if ($('a.pushed').click().length == 0) {
          $('a.scan:first').click();
        }
      } else if (ui.panel.id == 'transcript') {
        footnote.setup();
      }
    },
  });

});