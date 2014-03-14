"use strict";

var Backbone = require('../backbone')
  , $ = require('jquery')
  , NoteSectionListView = require('./note_section_list')
  , RelatedTopicsView = require('./related_topics')


module.exports = Backbone.View.extend({
  events: {
    'click #note-description': 'editDescription',
    'change select[name="note-status"]': 'updateStatus',
  },

  initialize: function (options) {
    var note = this.model

    this.sectionListView = new NoteSectionListView({ model: note });
    this.topicListView = new RelatedTopicsView({ collection: note.related_topics });

    this.listenTo(this.topicListView.collection, 'add', this.refreshRelatedTopics)
    this.listenTo(this.topicListView.collection, 'remove', this.refreshRelatedTopics)
    
    /*
    this.licenseChooser = new EditorsNotes.Views.NoteLicense({
      model: note,
      el: that.$();
    });
    */

  },

  render: function () {
    var that = this
      , template = require('../templates/note.html')

    this.$el.empty().html(template({ note: that.model }));
    this.sectionListView.setElement( that.$('#note-sections') );
    this.sectionListView.render()

    this.topicListView.$el.appendTo( that.$('#note-authorship') );
  },

  refreshRelatedTopics: function () {
    var topicNames = this.model.related_topics.map(function (model) {
      return model.get('name');
    });
    this.model.set('related_topics', topicNames).save();
  },

  updateStatus: function (e) {
    this.model.set('status', e.target.value).save();
  },

  editDescription: function () {
    var $description = this.$('#note-description')
      , note = this.model
      , html

    if ($description.hasClass('active')) return;

    $description.addClass('active').find('> :first-child').editText({
      afterInit: function () {
        var that = this;

        html = ''
          + '<div class="row">'
            + '<a class="btn btn-primary save-changes pull-right">Save</a>'
          + '</div>'

        $(html).insertAfter(this.editor.composer.iframe).on('click .btn', function (e) {
          setTimeout(function () { that.destroy() }, 0);
        });
      },
      destroy: function (val) {
        note.set('content', val).save().done(function (resp) {
          $description.removeClass('active').html(resp.content);
        });
      }
    });
  }

});
