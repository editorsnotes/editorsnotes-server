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
  //$('textarea[id!=id_content]').wymeditor(wymconfig);

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
      var selected_text = wym._iframe.contentWindow.getSelection().toString();
      if (selected_text) {
        wym.status('&nbsp;');
        var stamp = wym.uniqueStamp();
        stamps.push(stamp);
        wym._exec(WYMeditor.CREATE_LINK, stamp);
        $('a[href=' + stamp + ']', wym._doc.body).attr(WYMeditor.CLASS, 'footnote')
        django.jQuery('#footnotes-group .add-row a').click();
      } else {
        wym.status('You must select some text to add a footnote.');
      }
      /*
          // TODO: pop up a footnote creation dialog, and somehow get 
          // back the footnote uri when we're done.
          var footnote_uri = ; 
          wym._exec(WYMeditor.CREATE_LINK, footnote_uri);
          $("a[href=" + footnote_uri + "]", 
            wym._doc.body).attr(WYMeditor.CLASS, 'footnote-link');
          return false;
        */
    });
  };

  // Initialize content WYMeditor.
  $('textarea#id_content').wymeditor(wymconfig_content);

  // Initialize footnote WYMeditor.
  $('body').bind('footnoterowadded', function(e, row) {
    // Can't use the row directly since it was loaded by the 
    // Django jQuery instance, which doesn't have wymeditor.
    var row_id = row.attr('id');
    $('#' + row_id + ' textarea').wymeditor(wymconfig);
    $('#id_' + row_id + '-stamp').attr('value', stamps.shift());
  });

  // Initialize timeago.
  $('time.timeago').timeago();
});
