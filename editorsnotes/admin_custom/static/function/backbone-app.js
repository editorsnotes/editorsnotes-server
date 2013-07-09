EN = EditorsNotes

EN.Views = {}
EN.Models = {}
EN.Templates = {}

var wysihtml5BaseOpts = {
  parserRules: wysihtml5ParserRules,
  stylesheets: ['/static/function/wysihtml5/stylesheet.css'],
  useLineBreaks: false
}

var oldSync = Backbone.sync;
Backbone.sync = function (method, model, options) {
  options.beforeSend = function (xhr) {
    var token = $('input[name="csrfmiddlewaretoken"]').val();
    xhr.setRequestHeader('X-CSRFToken', token);
  }
  return oldSync(method, model, options);
};


/**************************************
 *
 * Models
 *
 **************************************/
EN.Models['Project'] = Backbone.Model.extend({
  initialize: function (attributes, options) {
    var slug = (attributes && attributes.slug) || (function (pathname) {
      var match = pathname.match(/^\/(?:api\/)?projects\/([^\/]+)/)
      return match && match[1];
    })(document.location.pathname);

    if (!slug) {
      throw new Error('Could not get project without url or argument');
    }

    this.set('slug', slug);

    this.documents = new EN.Models.DocumentCollection([], { project: this });
    this.notes = new EN.Models.NoteCollection([], { project: this });
    //this.topics = new EN.Models.TopicCollection([], { project: this });
  },
  url: function () {
    return '/api/projects/' + this.get('slug') + '/';
  }
});

EN.Models['Document'] = Backbone.Model.extend({
  initialize: function () {
    this.project = (this.collection && this.collection.project);
    if (!this.project) {
      throw new Error('Add notes through a project instance');
    }
  },
  url: function () {
    var origURL = Backbone.Model.prototype.url.call(this);
    return origURL.slice(-1) === '/' ? origURL : origURL + '/';
  },
  defaults: {
    description: null,
    zotero_data: null,
    topics: [],
  },
  toCSLJSON: function () {
    if (!this.get(zotero_data)) return {};
    return EditorsNotes.zotero.zoteroToCSL(this.get(zotero_data));
  },
  toFormattedCitation: function () {
    var citation = makeCitation(this.toCSLJSON());
    if (citation.match(/reference with no printed form/)) {
      citation = '';
    }
    return citation;
  }
});

EN.Models['DocumentCollection'] = Backbone.Collection.extend({
  model: EN.Models.Document,
  initialize: function (models, options) {
    this.project = this.project || options.project;
  },
  url: function () {
    return this.project.url() + 'documents/';
  }
});


var NoteSection = Backbone.Model.extend({
  idAttribute: 'section_id',
  initialize: function () {
    this.project = this.collection.project;
  },
  url: function () {
    return this.isNew() ?
      this.collection.url :
      this.collection.url + 's' + this.get('section_id') + '/';
  }
});

var NoteSectionList = Backbone.Collection.extend({
  model: NoteSection,
  initialize: function (models, options) {
    this.project = options.project;
  },
  parse: function (response) {
    return response.sections;
  }
});

EN.Models['Note'] = Backbone.Model.extend({
  url: function() {
    var origURL = Backbone.Model.prototype.url.call(this);
    return origURL.slice(-1) === '/' ? origURL : origURL + '/';
  },
  defaults: {
    'title': '',
    'content': '',
    'status': '1',
    'section_ordering': [],
    'topics': []
  },
  initialize: function (options) {
    var that = this;

    this.project = (this.collection && this.collection.project);
    if (!this.project) {
      throw new Error('Add notes through a project instance');
    }

    this.sections = new NoteSectionList([], {
      url: that.url(),
      project: this.project
    });
    this.sections.comparator = function (section) {
      var ordering = that.get('section_ordering');
      return ordering.indexOf(section.id);
    }
    this.topics = [];
  },
  parse: function (response) {
    var topicNames = response.topics.map(function (t) { return t.name });

    this.sections.set(response.sections);
    this.set('topics', topicNames);

    delete response.sections;
    delete response.topics;

    return response
  }
});

EN.Models['NoteCollection'] = Backbone.Collection.extend({
  model: EN.Models.Note,
  url: function () {
    return this.project.url() + 'notes/';
  },
  initialize: function (models, options) {
    this.project = options.project;
  }
});



/**************************************
 *
 * Templates
 *
 **************************************/
EN.Templates['add_item_modal'] = _.template(''
  + '<div class="modal-header">'
    + '<button type="button" class="close" data-dismiss="modal">&times;</button>'
    + '<h3>Add <%= type %></h3>'
  + '</div>'
  + '<div class="modal-body">'
    + '<textarea class="item-text-main" style="width: 98%; height: 40px;"></textarea>'
  + '</div>'
  + '<div class="modal-footer">'
    + '<img src="/static/style/icons/ajax-loader.gif" class="hide loader-icon pull-left">'
    + '<a href="#" class="btn" data-dismiss="modal">Cancel</a>'
    + '<a href="#" class="btn btn-primary btn-save-item">Save</a>'
  + '</div>')

EN.Templates['add_or_select_item'] = _.template(''
  + '<input style="width: 550px" type="text" class="<%= type %>-autocomplete" '
  + 'placeholder="Type to search for a <%= type %>, or add one using the icon to the right."'
  + ' />'
  + '<a class="add-new-object" href="#"><i class="icon-plus-sign"></i></a>')

EN.Templates['zotero/item_type_select'] = _.template(''
  + '<h5>Select an item type: </h5>'
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

EN.Templates['note_sections/citation'] = _.template(''
  + '<div class="citation-document">'
    + '<i class="icon-file"></i> '
    + '<div class="citation-document-item"'
        + '<% if (ns.document) { %>data-url="<%= ns.document %>"<% } %>>'
      + '<% if (ns.document) { print(ns.document_description) } %>'
    + '</div>'
  + '</div>'
  + ''
  + '<div class="note-section-content">'
    + '<%= ns.content %>'
  + '</div>')

EN.Templates['note_sections/note_reference'] = _.template(''
  + '<div class="note-reference-note">'
    + '<i class="icon-pencil"></i> '
    + '<div class="note-reference-note-container">'
      + '<% if (ns.note_reference) { %>'
        + '<span data-url="<%= ns.note_reference %>" class="note-reference-note">'
          + '<%= ns.note_reference_title %>'
        + '</span>'
      + '<% } %>'
    + '</div>'
  + '</div>'
  + ''
  + '<div class="note-section-content">'
    + '<%= ns.content %>'
  + '</div>')

EN.Templates['note_sections/text'] = _.template(''
  + '<div class="note-section-content">'
    + '<%= ns.content %>'
  + '</div>')

/**************************************
 *
 * Views
 *
 **************************************/

EN.Views['AddSectionToolbar'] = Backbone.View.extend({
  initialize: function (opts) {
    this.note = opts.note;
    this.render();
    this.$btn = this.$('button');
    this.$btnText = this.$btn.find('span');
    this.$loader = this.$btn.find('img');

    this.listenTo(this.note.sections, 'change', this.enableButton);
    this.listenTo(this.note.sections, 'sync removeEmpty', this.disableButton);
    this.listenTo(this.note.sections, 'request', this.showLoading);

  },
  events: {
    'click .add-section': 'addSection'
  },

  render: function () {
    this.$el.attr('id', 'citation-edit-bar');
    this.$el.append(''
      + '<h4>Add section: </h4>'
      + '<a class="add-section" data-section-type="citation">Citation</a>'
      + '<a class="add-section" data-section-type="text">Text</a>'
      + '<a class="add-section" data-section-type="note_reference">Reference to a note</a>'
      + '<button disabled="disabled" class="btn pull-right">'
        + '<span>No changes to save</span>&nbsp;'
        + '<img style="display: none" src="/static/style/icons/ajax-loader.gif">'
      + '</button>')
  },

  enableButton: function (sec) {
    sec.isDirty = true;
    this.$btn.prop('disabled', false).addClass('btn-primary');
    this.$btnText.text('Save changes');
  },

  disableButton: function (model) {
    if (model) model.isDirty = false;
    this.$btn.prop('disabled', 'disabled').removeClass('btn-primary');
    this.$loader.hide();
    this.$btnText.text('All changes saved');
  },

  showLoading: function () {
    this.$btn.prop('disabled', 'disabled').removeClass('btn-primary');
    this.$loader.show();
    this.$btnText.text('Saving...');
  },

  addSection: function (e) {
    var sectionType = $(e.currentTarget).data('sectionType')
      , idx = 0

    e.preventDefault();
    this.note.sections.add({'section_type': sectionType}, {'at': idx, 'sort': false});

  }
});

EN.Views['NoteSectionList'] = Backbone.View.extend({
  initialize: function (options) {
    var that = this;

    this.note = this.model;
    this.project = this.project;

    this._sectionViews = [];
    this.addView = new EN.Views.AddSectionToolbar({ note: this.note });
    this.addView.$el.insertBefore(this.$el);


    this.listenTo(this.note.sections, 'add', this.addSection);
    this.listenTo(this.note.sections, 'remove', this.removeSection);
    this.listenTo(this.note.sections, 'set', this.render);
    this.listenTo(this.note.sections, 'deactivate', this.deactivateSections);

    this.listenTo(this.note.sections, 'sync', this.saveOrder)

    this.note.fetch();
    this.render();
  },

  render: function () {
    var $el = this.$el.empty();

    this._rendered = true;
    this._sectionViews.forEach(function (sectionView) {
      $el.append(sectionView.el);
    });

  },

  addSection: function (section) {

    var idx = section.collection.indexOf(section)
      , SectionView = EN.Views['sections/' + section.get('section_type')]
      , view = new SectionView({ model: section })
      , target

    view.$el.data('sectionCID', view.model.cid);
    this._sectionViews.splice(idx, 0, view);

    if (!this._rendered) return;

    if (idx === 0) {
      this.$el.prepend(view.el);
    } else {
      target = this.$el.children()[idx - 1];
      view.$el.insertAfter(target);
    }

    if (section.isNew()) view.$el.trigger('click');
  },

  removeSection: function (section) {
    var that = this
      , sectionOrdering = this.note.get('section_ordering')
      , sectionViews = _(that._sectionViews)
      , viewToRemove

    viewToRemove = sectionViews.find(function (view) {
      return view.model === section
    });

    this._sectionViews = sectionViews.without(viewToRemove);

    sectionOrdering.pop(section.id);
    this.note.set('section_ordering', sectionOrdering);
  },

  deactivateSections: function (e) {
    var that = this;
    this._sectionViews.forEach(function (view) {
      view.deactivate.call(view);
    });
  },

  saveOrder: function () {
    var that = this
      , noteOrdering = this.note.get('section_ordering')
      , viewOrdering = []

    this._sectionViews.forEach(function (view) {
      if (view.model.id) viewOrdering.push(view.model.id);
    });

    if (noteOrdering.join('') !== viewOrdering.join('')) {
      this.note.set('section_ordering', viewOrdering);
      this.note.save();
    }

  }

});

/*
 * Base view for all note sections. Children must define the following methods:
 *
 * `isEmpty`
 */

EN.Views['NoteSection'] = Backbone.View.extend({
  tagName: 'div',
  className: 'note-section',
  isActive: false,

  events: {
    'click': 'edit',
  },

  initialize: function () {
    this.render();
    this.$el.addClass('note-section-' + this.model.get('section_type'));
  },

  render: function () {
    var that = this
      , sectionType = this.model.get('section_type')
      , template = EN.Templates['note_sections/' + sectionType]

    this.$el.html( template({ns: that.model.toJSON()}) );
    this.afterRender && this.afterRender.call(this);
  },

  edit: function () {
    var that = this
      , html

    if (this.isActive) return;

    this.model.collection.trigger('deactivate');

    this.isActive = true;
    this.$el.addClass('note-section-edit-active');
    this.editTextContent();

    html = ''
      + '<div class="edit-row">'
        + '<a class="btn btn-primary save-section pull-right">OK</a>'
        + '<a class="btn btn-danger delete-section">Delete section</a>'
      + '</div>'

    $(html)
      .appendTo(this.$el)
      .on('click .btn', function (e) {
        var deleteSection = $(e.target).hasClass('delete-section');
        setTimeout(function () { that.deactivate.call(that, deleteSection); }, 10);
      });

    return;
  },

  deactivate: function (deleteModel) {
    var collection;

    if (!this.isActive) return;

    this.isActive = false;
    this.$el.removeClass('note-section-edit-active');
    this.deactivateTextContent();

    if (this.isEmpty() || deleteModel) {
      collection = this.model.collection
      this.remove();
      this.model.destroy({
        success: function (model) {
          collection.remove(model);
          collection.trigger('removeEmpty');
        }
      });
    } else if (this.model.isDirty) {
      this.model.save();
    }

    return;
  },

  editTextContent: function () {
    var that = this
      , content = this.model.get('content')
      , textareaID = 'edit-section-' + this.model.cid
      , $content = this.$('.note-section-content')
      , $textarea
      , toolbar
    
    $textarea = $('<textarea>')
      .attr('id', textareaID)
      .css({
        'margin-bottom': '8px',
        'width': '99%',
        'height': (function (h) {
          return (h < 380 ? h : 380) + 120 + 'px';
        })($content.innerHeight())
      })
      .val(content)
      .appendTo(this.$el);

    $content.hide();

    toolbar = $('#note-section-toolbar').clone()
      .attr('id', textareaID + '-toolbar')
      .insertBefore($textarea)
      .show();

    // TODO: button edit row
    that.contentEditor = new wysihtml5.Editor(textareaID, _.extend({
      toolbar: textareaID + '-toolbar'
    }, wysihtml5BaseOpts));
    that.contentEditor.on('input', function () {
      that.model.set('content', that.contentEditor.getValue().replace('<br>', '<br/>'));
    });
  },

  deactivateTextContent: function (saveModelChanges) {
    var saveChanges = saveModelChanges === undefined ? true : !!saveChangesOpt
      , contentValue = this.contentEditor.getValue().replace('<br>', '<br/>')
      , toRemove = [
        'iframe.wysihtml5-sandbox',
        'input[name="_wysihtml5_mode"]',
        '.btn-toolbar',
        '.edit-row',
        'textarea'
      ]

    if (saveChanges) {
      this.model.set('content', contentValue || null);
      this.$('.note-section-content').html(contentValue);
    }
    this.$('.note-section-content').show();

    this.$(toRemove.join(',')).remove();
  }
  
});

EN.Views['sections/citation'] = EN.Views.NoteSection.extend({
  afterRender: function () {
    var that = this
      , addDocumentView
      , $documentContainer

    if (!this.model.isNew()) return;

    selectDocumentView = new EN.Views.SelectDocument({ project: this.model.project });
    $documentContainer = this.$('.citation-document-item')
      .html(selectDocumentView.el);

    this.listenToOnce(selectDocumentView, 'documentSelected', function (doc) {
      $documentContainer.html(doc.get('description'));
      that.model.set('document_description', doc.get('description'));
      that.model.set('document', doc.url());
      selectDocumentView.remove();
    });
  },
  isEmpty: function () {
    return !this.model.has('document');
  }
});

EN.Views['sections/note_reference'] = EN.Views.NoteSection.extend({
  afterRender: function () {
    var that = this
      , addNoteView
      , $noteContainer

    if (!this.model.isNew()) return;

    addNoteView = new EN.Views.SelectNote({ project: this.model.project });
    $noteContainer = this.$('.note-reference-note-container')
      .html(addNoteView.el);

    this.listenToOnce(addNoteView, 'noteSelected', function (note) {
      $noteContainer.html(note.get('title'));
      that.model.set('note_reference', note.url());
      that.model.set('note_reference_title', note.get('title'));
      addNoteView.remove();
    });
  },
  isEmpty: function () {
    return !this.model.has('note_reference');
  }
});

EN.Views['sections/text'] = EN.Views.NoteSection.extend({
  isEmpty: function () {
    return !this.model.get('content');
  }
})

/*
 * Base view for selecting items. Includes an autocomplete input and a button
 * to launch a modal for adding an item inline. Inheriting views must define
 * an `addItem` method to handle creating & rendering that modal.
 *
 * Options:
 *    project (required): slug of the project currently being worked on
 *    autocompleteopts: object defining settings for the autocomplete input
 */
EN.Views['SelectItem'] = Backbone.View.extend({
  events: {
    'click .add-new-object': 'addItem'
  },
  initialize: function (options) {
    var that = this
      , url

    this.project = options.project;
    url = this.autocompleteURL.call(this)

    this._autocompleteopts = _.extend({
      select: that.selectItem.bind(that),
      appendTo: '#note-sections-edit-blah',
      minLength: 2,
      source: function (request, response) {
        $.getJSON(url, {'q': request.term}, function (data) {
          response(data.results.map(function (item) {
            item.label = item[that.labelAttr || 'title'];
            return item;
          }));
        });
      },
    }, that.autocompleteopts || {})

    this.render();
  },
  render: function () {
    var that = this
      , $input

    this.$el.html(EN.Templates.add_or_select_item({type: that.type}));

    $input = this.$('input');
    $input.autocomplete(that._autocompleteopts)
      .data('autocomplete')._renderItem = function (ul, item) {
        return $('<li>')
          .data('item.autocomplete', item)
          .append('<a>' + item.label + '</a>')
          .appendTo(ul)
      }
  }
});

EN.Views['SelectDocument'] =  EN.Views.SelectItem.extend({
  type: 'document',
  labelAttr: 'description',
  autocompleteURL: function () { return this.project.url() + 'documents/' },
  selectItem: function (event, ui) {
    this.trigger('documentSelected', this.project.documents.add(ui.item).get(ui.item.id));
  },
  addItem: function (e) {
    var that = this
      , addView = new EN.Views.AddDocument({ project: this.project });

    this.listenTo(addView.model, 'sync', function (item) {
      that.trigger('documentSelected', item);
    });

    e.preventDefault();
    addView.$el.appendTo('body').modal();
  }
});

EN.Views['SelectNote'] = EN.Views.SelectItem.extend({
  type: 'note',
  labelAttr: 'title',
  autocompleteURL: function () { return this.project.url() + 'notes/'; },
  selectItem: function (event, ui) {
    this.trigger('noteSelected', this.project.notes.add(ui.item).get(ui.item.id));
  },
  addItem: function (e) {
    var addView = new AddNoteView({ project: this.opts.project });

    e.preventDefault();
    addView.$el.appendTo('body').modal();
  }
});


/*
 * Base view for all views adding items in a modal
 *
 * Must create saveItem method
 *
 * options:
 *    height
 *    minHeight
 *    width
 */
EN.Views['AddItem'] = Backbone.View.extend({
  renderModal: function () {
    var that = this
      , widget = EN.Templates.add_item_modal({ type: 'document' })
      , $loader

    this.$el.html(widget).addClass('modal');
    $loader = this.$('.loader-icon');

    this.$el
      .on('ajaxStart', function () { $loader.show(); })
      .on('ajaxStop', function () { $loader.hide(); })
      .on('hidden', that.remove.bind(that))
      .on('shown', that.setModalSize.bind(that))
      .on('click', '.btn-save-item', that.saveItem.bind(that));
  },

  setModalSize: function () {
    var that = this
      , $w = $(window)
      , modalHeight
      , bodyHeight
      , modalPosition = {
        'my': 'top',
        'at': 'top',
        'of': $w,
        'collision': 'none',
        'offset': '0 20'
      }

    modalHeight = this.options.height || (function () {
      var windowHeight = $w.height() - 50
        , minHeight = that.options.minHeight || 500

      return windowHeight > minHeight ? windowHeight : minHeight;
    })();

    bodyHeight = modalHeight
      - this.$('.modal-header').innerHeight()
      - this.$('.modal-footer').innerHeight()
      - (function (b) {
          var ptop = parseInt(b.css('padding-top'))
            , pbot = parseInt(b.css('padding-bottom'));
          return ptop + pbot;
        })(this.$('.modal-body'))
      - 2; // border

    this.$el.css({
      position: 'absolute',
      width: this.options.width || 840,
      height: modalHeight
    }).position(modalPosition).position(modalPosition);

    this.$('.modal-body').css({
      'height': bodyHeight,
      'max-height': bodyHeight
    });

  }
});

EN.Views['AddDocument'] = EN.Views.AddItem.extend({
  initialize: function (options) {
    this.model = options.project.documents.add({}, {at: 0}).at(0);
    this.render();
    this.$('.modal-body').append('<div class="add-document-zotero-data">');
    this.zotero_view = new EN.Views.EditZoteroInformation({
      el: this.$('.add-document-zotero-data')
    });
  },

  render: function () { this.renderModal(); },

  saveItem: function () {
    var that = this
      , data = { description: this.$('.item-text-main').val() }
      , zotero_data = this.zotero_view.getZoteroData();

    if (!_.isEmpty(zotero_data)) {
      data.zotero_data = JSON.stringify(zotero_data);
    }

    this.model.set(data);
    this.model.save(data, {
      success: function () { that.$el.modal('hide') }
    });

  }
});

EN.Views['EditZoteroInformation'] = Backbone.View.extend({
  events: {
    'change .item-type-select': function (e) {
      this.renderZoteroForm(e.currentTarget.value);
    },
    'click add-creator': 'addCreator',
    'click remove-creator': 'removeCreator',
    'input .zotero-entry': 'sendZoteroData',
  },

  initialize: function () {
    var that = this

    this.citeprocWorker = new Worker('/static/function/citeproc-worker.js');
    this.citeprocWorker.addEventListener('message', function (e) {
      that.trigger('updateCitation', e.data.citation);
    });
    this.on('updateCitation', this.updateCitation);

    this.render();

    $.getJSON('/api/document/itemtypes/')
      .done(function (itemTypes) {
        var select = EN.Templates['zotero/item_type_select'](itemTypes);
        that.$el.html('<hr />' + select);
        that.$('select').prop('selectedIndex', -1);
      })
      .error(function () {
        console.error('Could not fetch item types from server.');
      });

  },

  renderZoteroForm: function (itemType) {
    var that = this
      , $input = this.$('input').hide()

    $.get('/api/document/template/?itemType=' + itemType)
      .done(function (template) {
        var $template = $(template).filter('#zotero-information-edit');
        that.$el
          .html('<hr />' + $template.html())
          .find('.zotero-entry-delete').remove();
      })
      .fail(function () {
        alert('Could not retrieve template');
        $input.show()
      });
  },

  getZoteroData: function () {
    var that = this;
    return EditorsNotes.zotero.zoteroFormToObject(that.$el);
  },

  sendZoteroData: function () {
    var zoteroData = this.getZoteroData();
    this.citeprocWorker.postMessage({zotero_data: zoteroData});
  },

  updateCitation: function (citation) {
    var textarea = $('.item-text-main');

    textarea.val(citation);
  }

});
