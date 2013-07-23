function backboneInit(e) {
  var project = new EditorsNotes.Models.Project()
    , noteID = document.location.pathname.match(/notes\/(\d+)\//)[1]
    , note = project.notes.add({ id: noteID }).get(noteID)
    , view

  e.preventDefault();

  function flash() {
    var $container = $('#note-sections-container');

    $('<div>&nbsp;</div>')
      .css({
        'opacity': .90,
        'height': $container.height(),
        'width': $container.width(),
        'background-color': 'green',
        'position': 'absolute'
      })
      .appendTo('body')
      .position({ 'my': 'top', 'at': 'top', 'of': $container })
      .animate({ opacity: 0 }, 250, function () { $(this).remove() });
  }

  view = new EditorsNotes.Views.NoteSectionList({
    el: '#note-sections-container',
    model: note
  });

  view.model.once('sync', function () {
    $('#tabs [href="#note-tab"]').one('shown', flash).trigger('click');
  });
}

$(document).ready(function() {

  var url = $.param.fragment();
  if ( url == '' ) {
    window.location.replace(window.location.href + '#about');
    url = $.param.fragment();
  }

  var tabs = $('#tabs a');

  tabs.click(function(e) {
    e.preventDefault();
    var index = $(this).attr('href').match(/#(.+)-tab/)[1];
    $.bbq.pushState(index, 2);
  });

  $(window).bind('hashchange', function(e) {
    var index = $.bbq.getState();
    $.each(index, function(key, value) {
      var tabToOpen = tabs.filter('a[href*="' + key + '"]');
      if (tabToOpen.length > 0) {
        tabToOpen.tab('show');
      }
    });
  }).trigger('hashchange');

  $('.edit-note-sections').on('click', backboneInit);

});
