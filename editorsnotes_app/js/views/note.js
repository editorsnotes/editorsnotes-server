"use strict";

var Backbone = require('../backbone')
  , $ = require('jquery')


module.exports = Backbone.View.extend({
  events: {
    'click #note-description': 'editDescription'
  },

  initialize: function (options) {
    var note = this.model
      , NoteSectionListView = require('./note_section_list')

    this.sectionListView = new NoteSectionListView({ model: note });
    
    /*
    this.topicListView = new EditorsNotes.Views.RelatedTopicList({
      model: note,
      el: that.$('#note-related-topics');
    });
    */

    /*
    this.licenseChooser = new EditorsNotes.Views.NoteLicense({
      model: note,
      el: that.$();
    });
    */

  },

  render: function () {
    var that = this
      , template = require('../templates/note')

    this.$el.empty().html(template({ note: that.model.toJSON() }));
    this.sectionListView.setElement( that.$('#note-sections') );
    this.sectionListView.render()
    // this.topicListView.render();
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
