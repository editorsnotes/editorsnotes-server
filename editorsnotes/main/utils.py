# -*- coding: utf-8 -*-

import os.path
from lxml import etree
from isodate import datetime_isoformat

textify = etree.XSLT(etree.parse(
        os.path.abspath(os.path.join(os.path.dirname(__file__), 'textify.xsl'))))

def xhtml_to_text(xhtml):
    string = etree.tostring(textify(xhtml), method='text', encoding=unicode)
    if string: string = string.strip() 
    return string

def truncate(text, length=80):
    if len(text) <= length:
        return text
    l = text[:(length/2)].rsplit(' ', 1)[0]
    r = text[-(length/2):].split(' ', 1)
    if len(r) == 1:
        r = r[0]
    else:
        r = r[1]
    return l + u'... ' + r

def timeago(datetime):
    return '<time class="timeago" datetime="%s">%s</time>' % (
        datetime_isoformat(datetime), datetime.strftime('%I:%M%p, %b %d %Y'))

def prepend_space(element):
    element.addprevious(etree.Entity('nbsp'))
        
