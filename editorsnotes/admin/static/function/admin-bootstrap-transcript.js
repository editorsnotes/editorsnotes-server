$(document).ready(function () {
  var $formset = $('#footnote-formset')
    , editor

  function addFootnote(stamp, anchoredText) {
    $formset
      .one('formsetAppended', function (e, newFootnote) {
        var $newFootnote = $(newFootnote);

        $('.footnote-anchor', $newFootnote)
          .text(anchoredText);

        $newFootnote
          .removeClass('hide')
          .editText();
      })
      .appendFormset('.footnote-edit', {stamp: stamp.slice(1)});
  }

  $formset
    .on('click', '.footnote-edit:not(.section-edit-active)', function (e) {
      $(this).editText();
    });

  wysihtml5.commands.footnote = {
    exec: function(composer, command, param) {
      var selection = composer.selection.getSelection()
        , selectedText = selection.toString()
        , overlap = false
        , stamp = _.uniqueId('#newfootnote')

      if (this.state(composer, command)) {
        // Focus selected footnote for editing, maybe?

      } else {
        // Create a new footnote, both as an anchor in the transcript text and
        // a new footnote form to save.

        if (!selectedText){
          alert('Select text to create a footnote.');
          return;
        } 

        // Check if selected text overlaps with other footnotes
        $(composer.element).find('.footnote').each(function () {
          if (selection.containsNode(this, true)) {
            overlap = true;
            return;
          }
        });

        if (overlap) {
          alert('Footnotes can not overlap.');
          return;
        }

        wysihtml5.commands.createLink.exec(composer, 'createLink', {
          'class': 'footnote',
          'href': window.location.pathname + stamp // stamp
        });

        addFootnote(stamp, selectedText);
      }
    },
    state: function(composer, command) {
      var selection = composer.selection.getSelection()
        , parentElement

      if (!selection) {
        return false;
      }
  
      parentElement = selection.focusNode.parentElement;
      return (parentElement
              && parentElement.nodeName.toUpperCase() === 'A'
              && parentElement.classList.contains('footnote'))

    },
    value: function() {
      return undefined;
    }
  }

  editor = new wysihtml5.Editor('id_content', {
    toolbar: 'content-toolbar',

    parserRules: (function (rules) {
      var transcriptRules = rules;
      transcriptRules.tags.a = {
        check_attributes: {'href': 'src'}
      }
      transcriptRules.classes['footnote'] = 1;
      return transcriptRules;
    })(wysihtml5ParserRules),

    stylesheets: ['/static/function/wysihtml5/stylesheet.css']
  });

});
