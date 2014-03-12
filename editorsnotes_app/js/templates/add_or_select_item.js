var _ = require('underscore');

module.exports = _.template(''
  + '<input style="width: 550px" type="text" class="<%= type %>-autocomplete" '
  + 'placeholder="Type to search for a <%= type %>, or add one using the icon to the right."'
  + ' />'
  + '<a class="add-new-object" href="#"><i class="icon-plus-sign"></i></a>')
