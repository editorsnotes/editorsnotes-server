function backboneInit(e) {
  var project = new EditorsNotes.Models.Project()
    , noteID = document.location.pathname.match(/notes\/(\d+)\//)[1]
    , note = project.notes.add({ id: noteID }).get(noteID)
    , sectionView

    sectionView = new EditorsNotes.Views.NoteSectionList({
      model: note,
      el: '#note-sections'
    });

    sectionView.model.fetch()
      .done(function () { sectionView.render(); })
      .fail(function () { alert('error') })

}

$(document).ready(function() {
  $('<button class="btn-large btn-danger">EDIT</button>')
    .appendTo('body')
    .css('position', 'fixed')
    .on('click', function(e) { backboneInit(e); $(this).remove(); })
    .position({ my: 'right-64', at: 'right', of: window })
});
