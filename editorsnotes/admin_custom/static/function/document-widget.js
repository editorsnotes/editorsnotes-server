var documentWidgetTemplate = ''
  + '<div class="add-document-section add-document-header">'
    + '<button type="button" class="close">&times;</button>'
    + '<h3>Add document</h3>'
  + '</div>'
  + '<div class="add-document-section add-document-description">'
    + '<textarea></textarea>'
  + '</div>'
  + '<div class="add-document-section add-document-zotero-data">'
  + '</div>'

var itemTypeSelectTemplate = _.template(''
  + '<select class="item-type-select">'
    + ''
    + '<% if (common) { %>'
      + '<optgroup label="Common types">'
        + '<% common.forEach(function (commonType) { %>'
        + '<% var type = _.findWhere(itemTypes, {itemType: commonType}) %>'
        + '<option value="<%= type.itemType %>"><%= type.localized %></option>'
        + '<% }); %>'
      + '</optgroup>'
    + '<% } %>'
    + '<optgroup label="All types">'
      + '<% itemTypes.forEach(function (type) { %>'
      + '<option value="<%= type.itemType %>"><%= type.localized %></option>'
      + '<% }) %>'
    + '</optgroup>'
    + ''
  + '</select>')

function DocumentSelectorWidget(project) {
  var itemTypesPromise = $.getJSON('/api/document/itemtypes/');
  // var makeCitation = EditorsNotes.CSL.createCSLEngine('chicago_fullnote_bibliography2');

  var Document = Backbone.Model.extend({
    urlRoot: '/api/' + project + '/documents/',
    defaults: {
      description: null,
      zoteroData: '',
    },
    toCSLJSON: function () {
      if (!this.get(zoteroData)) return {};
      return EditorsNotes.zotero.zoteroToCSL(this.get(zoteroData));
    },
    toFormattedCitation: function () {
      var citation = makeCitation(this.toCSLJSON())
      if (citation.match(/reference with no printed form/)) {
        citation = '';
      }
      return citation;
    }
  });

  var DocumentWidgetView = Backbone.View.extend({
    events: {
      'change .item-type-select': function (e) {
        this.renderZoteroForm(e.currentTarget.value);
      },
      'click add-creator': 'addCreator',
      'click remove-creator': 'removeCreator',
      'click button.cancel': 'cancel',
      'click button.save': 'save',
    },

    initialize: function () {
      var that = this;

      itemTypesPromise.done(function (itemTypes) {
        that.$itemTypeSelect = $(itemTypeSelectTemplate(itemTypes));
        that.render();
      });
    },

    render: function () {
      var that = this;
      this.model = new Document();
      this.$el
        .html(documentWidgetTemplate)
        .appendTo('#note-sections-container');
      this.$itemTypeSelect
        .appendTo(this.$el.find('.add-document-zotero-data'))
        .prop('selectedIndex', -1);
    },

    renderZoteroForm: function (itemType) {
      var that = this
        , $container = this.$el.find('.add-document-zotero-data')

      this.$itemTypeSelect.hide();
      $.get('/api/document/template/?itemType=' + itemType)
        .done(function (template) {
          var $template = $(template).filter('#zotero-information-edit');
          $container.html($template.html());
        })
        .fail(function () {
          alert('Could not retrieve template');
        });
    },

    save: function () {
      this.model.save()
    },
    
    close: function () {
    }

  });

  return new DocumentWidgetView();
}
