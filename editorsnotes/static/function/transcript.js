$(document).ready(function () {
  var i = 1;
  $('a.footnote').each(function(index) {
    var note_id = $(this).attr('href').split('/').slice(-2,-1)[0];
    var note = $('div#note-' + note_id);
    var offset = note.offset();
    offset.top = $(this).offset().top;
    note.offset(offset).css('opacity', 0);
    $(this).mouseenter(function() {
      $('a.footnote[href!=' + $(this).attr('href') + ']').css('color', '#222');
      $('div.transcript-note:not(#note-' + note_id + ')').css('opacity', 0);
      $(this).css('color', 'red');
      note.animate({'opacity': 1}, 'fast');
    });
    $(this).focus(function() {
      $('div.transcript-note:not(#note-' + note_id + ')').css('opacity', 0);
      $(this).css('color', 'red');
      note.animate({'opacity': 1}, 'fast');
    });
    $(this).click(function() { return false; });
    $(this).append('<small><sup>' + i + '</sup></small>');
    note.find('p:first').prepend('<span class="note-number">' + i + '. </span>');
    i += 1;
  });
});