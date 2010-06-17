$(document).ready(function () {

  var stamps = [];

  var wymconfig = {
    skin: 'custom',
    toolsItems: [
      {'name': 'Bold', 'title': 'Strong', 'css': 'wym_tools_strong'}, 
      {'name': 'Italic', 'title': 'Emphasis', 'css': 'wym_tools_emphasis'},
      {'name': 'InsertOrderedList', 'title': 'Ordered_List', 'css': 'wym_tools_ordered_list'},
      {'name': 'InsertUnorderedList', 'title': 'Unordered_List', 'css': 'wym_tools_unordered_list'},
      {'name': 'Undo', 'title': 'Undo', 'css': 'wym_tools_undo'},
      {'name': 'Redo', 'title': 'Redo', 'css': 'wym_tools_redo'},
      {'name': 'CreateLink', 'title': 'Link', 'css': 'wym_tools_link'},
      {'name': 'Unlink', 'title': 'Unlink', 'css': 'wym_tools_unlink'},
      {'name': 'ToggleHtml', 'title': 'HTML', 'css': 'wym_tools_html'}
    ],
    updateSelector: 'input:submit',
    updateEvent: 'click',
    classesHtml: ''
  };

  var wymconfig_content = jQuery.extend(true, {}, wymconfig);

  // Initialize WYMeditors (except the content one).
  $('textarea').filter(function() {
    return this.id.match(/id_footnotes-\d+-content/);
  }).wymeditor(wymconfig);

  wymconfig_content.postInit = function(wym) {
    var button = ''
      + '<li class="wym_tools_footnote">'
      + '<a name="Footnote" title="Footnote" href="#"'
      + ' style="background-image:'
      + ' url(/media/function/wymeditor/skins/custom/footprint.png)">'
      + 'Footnote'
      + '</a></li>';
    $(wym._box).find(wym._options.toolsSelector + 
                     wym._options.toolsListSelector).append(button);
    $(wym._box).find('li.wym_tools_footnote a').click(function() {
      var selection = wym._iframe.contentWindow.getSelection();
      var selected_text = selection.toString();
      var overlap = false;
      //$(wym._iframe).contents().find('a.footnote').each(function(index) {
      $('a.footnote', wym._doc.body).each(function(index) {
        if (selection.containsNode(this, true)) {
          overlap = true;
          return false;
        }
      });
      if (overlap) {
        wym.status('Footnotes cannot overlap.');
      } else if (selected_text) {
        wym.status('&nbsp;');
        var stamp = wym.uniqueStamp();
        stamps.push(stamp);
        wym._exec(WYMeditor.CREATE_LINK, stamp);
        $('a[href=' + stamp + ']', wym._doc.body).attr(WYMeditor.CLASS, 'footnote')
        django.jQuery('#footnotes-group .add-row a').click();
      } else {
        wym.status('You must select some text to add a footnote.');
      }
    });

    // Friendlier labels on footnote rows.
    $('.dynamic-footnotes').each(function(index) {
      var row_id = $(this).attr('id');
      var footnote_id = $(this).find('#id_' + row_id + '-id').attr('value');
      var link = $('a[href="/footnote/' + footnote_id + '/"]', wym._doc.body);
      $(this).find('.inline_label').text(link.text());
    });

    $('body').bind('footnoterowadded', function(e, row) {
      var row_id = row.attr('id');
      row.find('#id_' + row_id + '-stamp').attr('value', stamps.shift());
      $('#' + row_id + ' textarea').wymeditor(wymconfig);
      $('html,body').animate({ scrollTop: row.offset().top - 100 }, 500);
    });

    $('body').bind('footnoterowremoved', function(e, row) {
      var row_id = row.attr('id');
      var stamp = row.find('#id_' + row_id + '-stamp').attr('value');
      var selection = wym._iframe.contentWindow.getSelection();
      selection.selectAllChildren($('a[href="' + stamp + '"]', wym._doc.body)[0]);
      wym._exec(WYMeditor.UNLINK)
      wym._iframe.contentWindow.focus();
      selection.collapseToStart();
    });
  };

  // Initialize content WYMeditor.
  $('textarea#id_content').wymeditor(wymconfig_content);

  // Initialize timeago.
  $('time.timeago').timeago();
});
