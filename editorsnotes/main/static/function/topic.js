$(document).ready(function() {
  var facetsInitiated = false;

  $('#tabs a').on('shown', function(e) { var targetPanel = e.currentTarget.hash;
    if (targetPanel.match(/documents/)) {
      if (!facetsInitiated) {
        $('#document-list').facet({
          fields: [
            {'key': 'itemtype', 'label': 'Item Type'},
            {'key': 'publicationtitle', 'label': 'Publication Title'},
            {'key': 'author', 'label': 'Author'},
            {'key': 'recipient', 'label': 'Recipient'},
            {'key': 'archive', 'label': 'Archive'},
            {'key': 'representations', 'label': 'Representations'}
          ],
          itemSelector: '.document'
        });
        facetsInitiated = true;
      }
    }
  });
});
