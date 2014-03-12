"use strict";

var EditorsNotes = window.EditorsNotes;

EditorsNotes.Views = {};
EditorsNotes.Models = {};
EditorsNotes.Templates = {};

EditorsNotes.Templates['wysihtml5_toolbar'] = require('./templates/wysihtml5_toolbar.html');
EditorsNotes.Models.Project = require('./models/project');
EditorsNotes.Views.Note = require('./views/note');
