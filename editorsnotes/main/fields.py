# -*- coding: utf-8 -*-

from django import forms
from django.db import models
from lxml import etree, html
from lxml.html.clean import Cleaner
from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape
from django.utils.encoding import force_unicode

cleaner = Cleaner(style=True)

class XHTMLWidget(forms.Textarea):
    def _format_value(self, value):
        if value is None:
            return ''
        if isinstance(value, html.HtmlElement):
            return etree.tostring(value)
        if isinstance(value, str) or isinstance(value, unicode):
            return value
        raise TypeError('%s cannot be formatted as XHTML' % value)
    def render(self, name, value, attrs=None):
        final_attrs = self.build_attrs(attrs, name=name)
        return mark_safe(u'<textarea%s>%s</textarea>' % (
                forms.util.flatatt(final_attrs),
                conditional_escape(force_unicode(self._format_value(value)))))

class XHTMLField(models.Field):
    description = 'A parsed XHTML fragment'
    __metaclass__ = models.SubfieldBase
    def __init__(self, *args, **kwargs):
        super(XHTMLField, self).__init__(*args, **kwargs)
    def db_type(self):
        return 'xml'
    def to_python(self, value):
        if isinstance(value, html.HtmlElement):
            return value
        if not (isinstance(value, str) or isinstance(value, unicode)):
            raise TypeError('%s cannot be parsed to XHTML' % type(value))
        if len(value) == 0:
            return None
        #value = re.sub(r'(&#13;\n)+', ' ', value)
        fragment = None
        try:
            fragment = html.fragment_fromstring(value)
        except etree.ParserError:
            fragment = html.fragment_fromstring(value, create_parent='div')
        return cleaner.clean_html(fragment)
    def get_db_prep_value(self, value):
        return etree.tostring(value)
    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)
    def formfield(self, **kwargs):
        defaults = {'widget': XHTMLWidget}
        defaults.update(kwargs)
        return super(XHTMLField, self).formfield(**defaults)
    def south_field_triple(self):
        return ('main.fields.XHTMLField', [], {})
