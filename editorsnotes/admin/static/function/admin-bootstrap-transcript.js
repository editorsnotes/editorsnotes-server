$(document).ready(function () {

  var editor = new wysihtml5.Editor('id_content', {
    toolbar: 'content-toolbar',
    parserRules: wysihtml5ParserRules,
    stylesheets: ['/static/function/wysihtml5/stylesheet.css']
  });

});
