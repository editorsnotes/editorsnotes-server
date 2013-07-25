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
  $('.edit-note-sections').on('click', backboneInit);
});
