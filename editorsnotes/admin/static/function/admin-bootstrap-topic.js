function bindCitation($citation) {
  var $input = $citation.find('.citation-document input')
    , prefix = 'id_' + $citation.prop('id')
    , autocompleteopts
    , editor = new wysihtml5.Editor(prefix + '-notes', {
      toolbar: $citation.prop('id') + '-toolbar',
      parserRules: wysihtml5ParserRules,
      useLineBreaks: false,
      stylesheets: ['/static/function/wysihtml5/stylesheet.css']
    });

  $('#' + prefix + '-toolbar').show();

  if ($input.length) {
    autocompleteopts = $.extend(EditorsNotes.baseAutoCompleteOpts, {
      select: function (e, ui) {
        if (!ui.item) return;
        $citation.find('.citation-document').addClass('document-selected');
        $input.replaceWith(ui.item.value);
        $citation.find('#' + prefix + '-document').val(ui.item.id);
      }
    });

    $input.autocomplete(autocompleteopts)
      .data('ui-autocomplete')._renderItem = function (ul, item) {
        return $('<li>')
          .data('ui-autocomplete-item', item)
          .append('<a>' + item.value + '</a>')
          .appendTo(ul)
      }
  }
}

function citationFormset($el) {
  var lastForm;

  this.$el = $el;
  this.$items = $el.find('#citation-items');
  this.managementForm = $el.find('#id_citation-TOTAL_FORMS');
  this.lastForm = this.$items.children().last();
  this.blankForm = this.lastForm.clone();
  this.counter = parseInt(this.managementForm.val(), 10);

  this.$items.children().each(function (idx, el) {
    bindCitation($(el));
  });

  return this;
}

citationFormset.prototype.addCitation = function () {
  var that = this
    , newForm
    , searchstr

  if (this.lastForm.is(':hidden')) {
    this.lastForm.removeClass('hide');
    return
  }

  newForm = this.blankForm.clone().removeClass('hide');
  searchstr = 'citation-' + (this.counter - 1) + '-'

  newForm.prop('id', 'citation-' + that.counter);
  newForm.find('[name^="' + searchstr + '"], [id^="' + searchstr + '"]')
    .each(function (idx, el) {
      if (el.name) el.name = el.name.replace('-' + (that.counter - 1) + '-', '-' + that.counter + '-');
      if (el.id) el.id = el.id.replace('-' + (that.counter - 1) + '-', '-' + that.counter + '-');
    });

  newForm.appendTo(that.$items);
  bindCitation(newForm);

  this.counter += 1;
  this.managementForm.val(that.counter);
}


$(document).ready(function() {
  var editor = new wysihtml5.Editor('id_summary', {
    toolbar: 'summary-toolbar',
    parserRules: wysihtml5ParserRules,
    useLineBreaks: false,
    stylesheets: ['/static/function/wysihtml5/stylesheet.css']
  });

  var formset = new citationFormset($('#citations-formset'));

  $('#add-citation').on('click', formset.addCitation.bind(formset));

});
