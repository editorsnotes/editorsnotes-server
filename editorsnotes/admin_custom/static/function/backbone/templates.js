EditorsNotes.Templates['note_section_list'] = _.template(''
    + '<div id="citation-edit-bar">'
      + '<h4>Add section: </h4>'
      + '<a class="add-section" data-section-type="citation">'
        + '<i class="icon-file"></i> Citation'
      + '</a>'
      + '<a class="add-section" data-section-type="text">Text</a>'
      + '<a class="add-section" data-section-type="note_reference">'
        + '<i class="icon-pencil"></i> Note reference'
      + '</a>'
      + '<span class="status-message">All changes saved.</span>'
      + '<img class="loader" src="/static/style/icons/ajax-loader.gif">'
    + '</div>'
    + '<div class="note-section-list"></div>')

EditorsNotes.Templates['add_item_modal'] = _.template(''
  + '<div class="modal-header">'
    + '<button type="button" class="close" data-dismiss="modal">&times;</button>'
    + '<h3>Add <%= type %></h3>'
  + '</div>'
  + '<div class="modal-body">'
    + '<% if (textarea) { %>'
    + '<textarea class="item-text-main" style="width: 98%; height: 40px;"></textarea>'
    + '<% } else { %>'
    + '<input type="text" class="item-text-main" style="width: 98%;" />'
    + '<% } %>'
  + '</div>'
  + '<div class="modal-footer">'
    + '<img src="/static/style/icons/ajax-loader.gif" class="hide loader-icon pull-left">'
    + '<a href="#" class="btn" data-dismiss="modal">Cancel</a>'
    + '<a href="#" class="btn btn-primary btn-save-item">Save</a>'
  + '</div>')

EditorsNotes.Templates['add_or_select_item'] = _.template(''
  + '<input style="width: 550px" type="text" class="<%= type %>-autocomplete" '
  + 'placeholder="Type to search for a <%= type %>, or add one using the icon to the right."'
  + ' />'
  + '<a class="add-new-object" href="#"><i class="icon-plus-sign"></i></a>')

EditorsNotes.Templates['zotero/item_type_select'] = _.template(''
  + '<h5>Common item types:</h5>'
  + ''
  + '<% if (common) { %>'
  + '<ul class="unstyled common-item-types">'
    + '<% common.slice(0, 6).forEach(function (commonType) { %>'
    + '<% var type = _.findWhere(itemTypes, { itemType: commonType }) %>'
    + '<li><a href="#" data-item-type="<%= type.itemType %>"><%= type.localized %></a></li>'
    + '<% }) %>'
  + '</ul>'
  + '<% } %>'
  + ''
  + '<h5>All types</h5>'
  + '<select class="item-type-select">'
    + '<% itemTypes.forEach(function (type) { %>'
    + '<option value="<%= type.itemType %>"><%= type.localized %></option>'
    + '<% }) %>'
  + '</select>')

EditorsNotes.Templates['note_sections/citation'] = _.template(''
  + '<div class="citation-side"><i class="icon-file"></i></div>'
  + ''
  + '<div class="citation-main">'
    + '<div class="citation-document">'
      + '<% if (ns.document) { print(ns.document_description) } %>'
    + '</div>'
    + '<div class="note-section-text-content"><%= ns.content %></div>'
  + '</div>')

EditorsNotes.Templates['note_sections/note_reference'] = _.template(''
  + '<div class="note-reference-side"><i class="icon-pencil"></a></div>'
  + ''
  + '<div class="note-reference-main">'
    + '<div class="note-reference-note">'
      + '<% if (ns.note_reference) { print(ns.note_reference_title) } %>'
    + '</div>'
    + '<div class="note-section-text-content"><%= ns.content %></div>'
  + '</div>')

EditorsNotes.Templates['note_sections/text'] = _.template(''
  + '<div class="note-section-text-content">'
    + '<%= ns.content %>'
  + '</div>')

EditorsNotes.Templates['wysihtml5_toolbar'] = _.template(''
  + '<div <% if (id) { print("id=\'" + id + "\' ") } %> class="btn-toolbar wysihtml5-toolbar">'
    + '<div class="btn-group">'
      + '<a class="btn" data-wysihtml5-command="bold">'
        + '<i class="icon-bold"></i>'
      + '</a>'
      + '<a class="btn" data-wysihtml5-command="italic">'
        + '<i class="icon-italic"></i>'
      + '</a>'
    +'</div>'
    + ''
  + '<% if (type !== "minimal" ) { %>'
    + '<div class="btn-group">'
      + '<a class="btn" data-wysihtml5-command="formatBlock" data-wysihtml5-command-value="p">'
        + '<strong>P</strong>'
      + '</a>'
      + ''
      + '<a class="btn" data-wysihtml5-command="formatBlock" data-wysihtml5-command-value="h1">'
        + '<strong>H1</strong>'
      + '</a>'
      + ''
      + '<a class="btn" data-wysihtml5-command="formatBlock" data-wysihtml5-command-value="h2">'
        + '<strong>H2</strong>'
      + '</a>'
      + ''
      + '<a class="btn" data-wysihtml5-command="formatBlock" data-wysihtml5-command-value="h3">'
        + '<strong>H3</strong>'
      + '</a>'
      + ''
      + '<a class="btn" data-wysihtml5-command="insertOrderedList">'
        + '<i class="icon-list-ol"></i>'
      + '</a>'
      + ''
      + '<a class="btn" data-wysihtml5-command="insertUnorderedList">'
        + '<i class="icon-list-ol"></i>'
      + '</a>'
    + '</div>'
  + '<% } %>'
  + '</div>')
